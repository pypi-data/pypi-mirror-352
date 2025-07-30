# Script containing the logic behind the java script feature extraction

from typing import Any
from typing import Union
from typing import Optional

from javalang.tree import Literal
from javalang.tree import MemberReference
from javalang.tree import MethodInvocation
from javalang.tree import ClassCreator
from javalang.tree import Assignment
from javalang.tree import BinaryOperation
from javalang.tree import ReferenceType
from javalang.tree import ForStatement
from javalang.tree import IfStatement
from javalang.tree import ReturnStatement
from javalang.tree import VariableDeclarator
from javalang.tree import StatementExpression
from javalang.tree import BlockStatement


def java_ast_extractor(node: Any) -> Optional[Union[str, dict, list]]:
    """
    Universal extractor for javalang AST nodes.

    Args:
        node: Any javalang AST node

    Returns:
        Extracted value based on node type:
        - Literal: value
        - MemberReference: variable name
        - MethodInvocation: function call details
        - ClassCreator: constructor call
        - Assignment: target and value
        - BinaryOperation: operator and operands
        - ReferenceType: type name
        - List: recursively extract each element
        - None: if node type is unsupported

    Example:
        >>> tree = javalang.parse.parse("class Test { void m() { int x = 3 + 5; } }")
        >>> body = list(tree.types[0].body)[0].body
        >>> java_ast_extractor(body[0].expression)
        {'left': '3', 'operator': '+', 'right': '5'}
    """

    if node is None:
        return None

    match node:
        case Literal():
            return (
                node.value.strip('"').strip("'")
                if isinstance(node.value, str)
                else node.value
            )

        case MemberReference():
            return node.member

        case MethodInvocation():
            return {
                "method": node.member,
                "qualifier": (
                    node.qualifier
                    if isinstance(node.qualifier, (str, type(None)))
                    else java_ast_extractor(node.qualifier)
                ),
                "arguments": [java_ast_extractor(arg) for arg in node.arguments],
                "selectors": [
                    java_ast_extractor(selector) for selector in node.selectors
                ]
                if node.selectors
                else None,
            }

        case ClassCreator():
            return {
                "type": java_ast_extractor(node.type),
                "arguments": [java_ast_extractor(arg) for arg in node.arguments],
                "body": [java_ast_extractor(body) for body in node.body]
                if node.body
                else None,
            }

        case Assignment():
            return {
                "expression": java_ast_extractor(node.expressionl),
                "value": java_ast_extractor(node.value),
                "operator": java_ast_extractor(node.type),
            }

        case BinaryOperation():
            return {
                "operandl": java_ast_extractor(node.operandl),
                "operator": java_ast_extractor(node.operator),
                "operandr": java_ast_extractor(node.operandr),
            }

        case ReferenceType():
            return ".".join(node.name)

        case ForStatement():
            return {
                "control": java_ast_extractor(node.control),
                "body": java_ast_extractor(node.body),
            }

        case IfStatement():
            return {
                "condition": java_ast_extractor(node.condition),
                "then_statement": java_ast_extractor(node.then_statement),
                "else_statement": java_ast_extractor(node.else_statement),
            }

        case ReturnStatement():
            return {
                "expression": java_ast_extractor(node.expression),
            }

        case VariableDeclarator():
            return {
                "name": java_ast_extractor(node.name),
                "dimensions": java_ast_extractor(node.dimensions),
                "initializer": java_ast_extractor(node.initializer),
            }

        case StatementExpression():
            return {
                "expression": java_ast_extractor(node.expression),
            }

        case BlockStatement():
            return [java_ast_extractor(statement) for statement in node.statements]

        case _:
            return None
