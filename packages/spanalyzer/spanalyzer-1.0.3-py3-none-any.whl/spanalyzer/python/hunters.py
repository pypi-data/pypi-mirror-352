# Script containing the logic behind the python script feature extraction

from ast import AST
from ast import Call
from ast import Name
from ast import Expr
from ast import Dict
from ast import List
from ast import Constant
from ast import Attribute
from ast import Subscript

from typing import Union
from typing import Optional
from typing import Any


def ast_extractor(node: AST) -> Optional[Union[str, dict, list, Any]]:
    """
    Universal AST node value extractor.

    Args:
        node: Any AST node

    Returns:
        Extracted value based on node type:
        - Constant: its value
        - Name: its id
        - Attribute: extracted value with attr
        - List: list of extracted values
        - Dict: dictionary of extracted key-value pairs
        - Call: function name and args
        - Expr: function name and args
        - Subscript: extracted value
        - None: for unsupported nodes

    Example:
        >>> ast_extractor(Constant(value='test'))
        'test'
        >>> ast_extractor(Attribute(value=Name(id='obj'), attr='method'))
        'obj.method'
    """

    match node:
        case Constant():
            return node.value

        case Name():
            return node.id

        case Attribute():
            base = ast_extractor(node.value)
            return f"{base}.{node.attr}" if base else node.attr

        case List():
            return [ast_extractor(elt) for elt in node.elts]

        case Dict():
            return {
                ast_extractor(k): ast_extractor(v)
                for k, v in zip(node.keys, node.values)
            }

        case Call():
            call_data = {
                "func": ast_extractor(node.func),
                "args": [ast_extractor(arg) for arg in node.args],
            }

            try:
                keywords = {kw.arg: ast_extractor(kw.value) for kw in node.keywords}

                if keywords:
                    call_data["keywords"] = keywords

            except (AttributeError, TypeError):
                pass

            return call_data

        case Expr():
            expr_data = {
                "func": ast_extractor(node.value.func),
                "args": [ast_extractor(arg) for arg in node.value.args],
            }

            try:
                keywords = {
                    kw.arg: ast_extractor(kw.value) for kw in node.value.keywords
                }
                if keywords:
                    expr_data["keywords"] = keywords
            except (AttributeError, TypeError):
                pass

            return expr_data

        case Subscript():
            return ast_extractor(node.value)

        case _:
            return None
