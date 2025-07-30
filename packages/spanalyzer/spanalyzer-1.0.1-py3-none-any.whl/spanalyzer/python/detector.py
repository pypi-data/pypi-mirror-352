# Script containing the Telemetry Detector

from typing import Dict
from typing import Optional

from ast import Call
from ast import Expr
from ast import Dict
from ast import Constant
from ast import NodeVisitor

from ast import walk

from spanalyzer.python.hunters import ast_extractor
from spanalyzer.python.constants.keywords import PythonTelemetryKeywords

from spanalyzer.utils.operations import remove_call_duplicates

from spanalyzer.constants.telemetry import TelemetryCall


class PythonTelemetryDetector(NodeVisitor):
    """
    This class will be used to sniff the telemetry calls in a script.

    It operates on single script at the time, and produces an output indicating if there's any telemetry
    call in the script.

    The telemetry calls at this stage are the ones that are commonly used (i.e. tracers, spans, attributes,
    events, exceptions, span ends, counters).
    """

    def __init__(self):
        """
        Initialize the PythonTelemetryDetector.

        This will initialize the output structure, and the operations that are of interest.
        """

        self.output = PythonTelemetryKeywords.get_attributes_structure()

        self.span_operations = {
            PythonTelemetryKeywords.START_SPAN,
            PythonTelemetryKeywords.START_AS_CURRENT_SPAN,
            PythonTelemetryKeywords.USE_SPAN,
        }

        self.attribute_operations = {
            PythonTelemetryKeywords.SET_ATTRIBUTE,
            PythonTelemetryKeywords.SET_ATTRIBUTES,
        }

        self.event_operations = {
            PythonTelemetryKeywords.ADD_EVENT,
            PythonTelemetryKeywords.ADD_EVENTS,
        }

    def _extract_name_from_args(self, node: Call) -> Optional[str]:
        """
        Extract name from first argument.

        Args:
            node [Call]: code node to be evaluated

        Returns:
            Optional[str]: name of the telemetry call
        """

        if not node.args:
            return None

        arg = node.args[0]

        return arg.value if isinstance(arg, Constant) else arg.id

    def call_switcher(self, call_type: str, node: Call):
        """
        This function will work as a switch to determine the type of call being made.

        According to the type of call being made, the function that will capture the telemetry details will be
        duly called.

        Args:
            call_type [str]: type of call being made
            node [Call]: code node to be evaluated
        """

        match call_type:
            case PythonTelemetryKeywords.GET_TRACER:
                if name := self._extract_name_from_args(node):
                    self.output["tracers"].append(
                        TelemetryCall(func=name, line_number=node.lineno)
                    )

            case _ if call_type in self.span_operations:
                if name := self._extract_name_from_args(node):
                    self.output["spans"].append(
                        TelemetryCall(
                            func=name,
                            line_number=node.lineno,
                        )
                    )

            case _ if call_type in self.attribute_operations:
                self.output["attributes"].append(
                    TelemetryCall(
                        func=call_type,
                        line_number=node.lineno,
                        args=ast_extractor(node),
                    )
                )

            case _ if call_type in self.event_operations:
                args = (
                    ast_extractor(node)
                    if isinstance(node, Expr)
                    else ast_extractor(node.args)
                )

                self.output["events"].append(
                    TelemetryCall(func=call_type, line_number=node.lineno, args=args)
                )

            case PythonTelemetryKeywords.ADD_COUNTER:
                self.output["counter"].append(
                    TelemetryCall(
                        func=call_type,
                        line_number=node.lineno,
                        args=ast_extractor(node),
                    )
                )

        self.generic_visit(node)

    def run(self, node: Call) -> Dict:
        """
        Method that can be seen as the heart of the PythonTelemetryDetector class.

        This method will be filtering the type of nodes that are of interest, and will be then calling
        the switcher method - that captures all the telemetry details spanalyzer is looking for.

        Args:
            node [Call]: code node to be evaluated

        Returns:
            Dict: dictionary containing the telemetry details
        """

        for node in walk(node):
            try:
                if isinstance(node, Call):
                    self.call_switcher(node.func.attr, node)

                if isinstance(node, Expr):
                    self.call_switcher(node.value.func.attr, node)

            except:
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
