# Script containing the logic that will be used to sniff the python scripts

from typing import Union

import ast
from ast import Str
from ast import Expr
from ast import parse
from ast import NodeVisitor
from ast import FunctionDef

from collections import namedtuple

FunctionSpecs = namedtuple(
    "FunctionSpecs", ["name", "docstring", "start_lineno", "end_lineno"]
)


class PythonScriptSniffer(NodeVisitor):
    """
    This class will scrape all the code from a python script and return the list of functions.

    Additionally, it will also capture some feature of those functions such as the number of lines
    of code, the number of arguments, etc.

    This will be used later on to determine the amount of telemetry calls in a script.

    Args:
        filename [str]: the code script to be sniffed
    """

    def __init__(self, filename: str):
        self.filename = filename
        self.functions_list = []

    def _has_docstring(self, node: FunctionDef) -> Union[str, None]:
        """
        Check if the function provided has a docstring.

        Before returning the docstring, it will be stripped of any leading and trailing whitespace.

        _Example_:

        Given the following function:
        ```python
        def function_with_docstring():
            '''
            This is a docstring
            '''
            pass
        ```

        The docstring will be returned as:
        ```python
        "This is a docstring"
        ```

        Args:
            node [FunctionDef]: the function that will be checked

        Returns:
            str: function docstring, None if it doesn't have one
        """

        has_docstring = lambda node: (
            len(node.body) > 0
            and isinstance(node.body[0], Expr)
            and isinstance(node.body[0].value, Str)
        )

        if has_docstring(node):
            return node.body[0].value.s.strip()

        return None

    def visit_FunctionDef(self, node: FunctionDef):
        """
        Capture the function definition and its additional features.

        Args:
            node [FunctionDef]: the function definition node
        """

        function_specs = FunctionSpecs(
            name=node.name,
            docstring=self._has_docstring(node),
            start_lineno=node.lineno,
            end_lineno=node.end_lineno,
        )

        self.functions_list.append(function_specs)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: FunctionDef):
        """
        Capture the async function definition and its additional features.

        Args:
            node [FunctionDef]: the function definition node
        """

        self.visit_FunctionDef(node)

    def run(self):
        """
        Run the sniffer over the script.

        This will firstly parse the script and then visit all the nodes to capture the function definitions.
        """

        with open(self.filename, "r") as file:
            tree = parse(file.read())

        self.visit(tree)
