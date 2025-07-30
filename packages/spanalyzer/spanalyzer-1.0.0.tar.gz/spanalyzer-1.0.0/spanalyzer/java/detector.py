# Script containing the logic behind the java script feature extraction

from typing import Any
from typing import Dict
from typing import Optional

from javalang.tree import MethodInvocation
from javalang.tree import ClassCreator

from spanalyzer.java.hunters import java_ast_extractor
from spanalyzer.java.constants.keywords import JavaTelemetryKeywords

from spanalyzer.utils.operations import remove_call_duplicates

from spanalyzer.constants.telemetry import TelemetryCall


class JavaTelemetryDetector:
    """
    This class sniffs for OpenTelemetry calls in Java code.

    It operates on a parsed javalang tree, detecting common telemetry-related calls like:
    - Tracers
    - Spans
    - Attributes
    - Events
    - Counters
    """

    def __init__(self):
        self.output = JavaTelemetryKeywords.get_attributes_structure()

        self.tracer_operations = {
            JavaTelemetryKeywords.GET_TRACER,
            JavaTelemetryKeywords.GET_TRACER_PROVIDER,
            JavaTelemetryKeywords.GET_GLOBAL_TRACER,
        }

        self.span_operations = {
            JavaTelemetryKeywords.SPAN_BUILDER,
            JavaTelemetryKeywords.START_SPAN,
            JavaTelemetryKeywords.MAKE_CURRENT,
            JavaTelemetryKeywords.END,
            JavaTelemetryKeywords.CURRENT_SPAN,
        }

        self.attribute_operations = {
            JavaTelemetryKeywords.SET_ATTRIBUTE,
            JavaTelemetryKeywords.SET_ATTRIBUTES,
        }

        self.event_operations = {
            JavaTelemetryKeywords.ADD_EVENT,
            JavaTelemetryKeywords.ADD_EVENTS,
        }

    def _extract_name_from_args(self, node: MethodInvocation) -> Optional[str]:
        """
        Extract name from first argument of a Java method call.
        """

        if not node.arguments:
            return None

        arg = node.arguments[0]

        return arg.value if hasattr(arg, "value") else str(arg)

    def call_switcher(self, method_name: str, node: MethodInvocation | ClassCreator):
        """
        Route method call to correct handler based on OpenTelemetry keyword.
        """

        match method_name:
            case _ if method_name in self.tracer_operations:
                if name := self._extract_name_from_args(node):
                    self.output["tracers"].append(
                        TelemetryCall(
                            func=name,
                            line_number=getattr(node, "position", None).line
                            if node.position
                            else -1,
                        )
                    )

            case _ if method_name in self.span_operations:
                if name := self._extract_name_from_args(node):
                    self.output["spans"].append(
                        TelemetryCall(
                            func=name,
                            line_number=getattr(node, "position", None).line
                            if node.position
                            else -1,
                        )
                    )

            case _ if method_name in self.attribute_operations:
                self.output["attributes"].append(
                    TelemetryCall(
                        func=method_name,
                        line_number=getattr(node, "position", None).line
                        if node.position
                        else -1,
                        args=java_ast_extractor(node),
                    )
                )

            case _ if method_name in self.event_operations:
                self.output["events"].append(
                    TelemetryCall(
                        func=method_name,
                        line_number=getattr(node, "position", None).line
                        if node.position
                        else -1,
                        args=java_ast_extractor(node),
                    )
                )

            case JavaTelemetryKeywords.COUNTER_ADD:
                self.output["counter"].append(
                    TelemetryCall(
                        func=method_name,
                        line_number=getattr(node, "position", None).line
                        if node.position
                        else -1,
                        args=java_ast_extractor(node),
                    )
                )

    def run(self, tree: Any) -> Dict:
        """
        Main runner that walks the Java AST and detects relevant telemetry calls.

        Args:
            tree (javalang parser tree): Parsed Java source tree

        Returns:
            Dict: Categorized dictionary of telemetry calls
        """

        for path, node in tree:
            try:
                if isinstance(node, MethodInvocation):
                    self.call_switcher(node.member, node)

                elif isinstance(node, ClassCreator) and node.body:
                    for body_expr in node.body:
                        if isinstance(body_expr, MethodInvocation):
                            self.call_switcher(body_expr.member, body_expr)

            except Exception:
                pass

        return {
            key: (
                remove_call_duplicates(val)
                if isinstance(val, list)
                and any(isinstance(item, TelemetryCall) for item in val)
                else []
            )
            for key, val in self.output.items()
        }
