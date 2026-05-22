import ast
import operator


# SAFE OPERATORS
operators = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def eval_expr(node):

    # NUMBER
    if isinstance(node, ast.Constant):

        return node.value

    # BINARY OPERATION
    elif isinstance(node, ast.BinOp):

        left = eval_expr(node.left)

        right = eval_expr(node.right)

        return operators[type(node.op)](
            left,
            right
        )

    # NEGATIVE NUMBER
    elif isinstance(node, ast.UnaryOp):

        operand = eval_expr(
            node.operand
        )

        return operators[type(node.op)](
            operand
        )

    else:

        raise TypeError(
            "Unsupported expression"
        )


def calculate(expression):

    try:

        # PARSE EXPRESSION
        node = ast.parse(
            expression,
            mode="eval"
        ).body

        # SAFE EVALUATION
        result = eval_expr(node)

        return str(result)

    except Exception:

        return (
            "Calculation failed."
        )


calculator_tool = {
    "name": "calculator",

    "description":
    "Performs safe mathematical calculations.",

    "function": calculate,

    "input_schema": {
        "expression": "string"
    }
}