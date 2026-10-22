import ast
import math
import operator
import re


BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}

UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def calculate(expression, degrees=True):
    expression = expression.strip().lower()

    if not expression:
        raise ValueError("Enter a calculation.")

    expression = expression.replace("×", "*")
    expression = expression.replace("÷", "/")
    expression = re.sub(
    r"(?<![=!<>])(\d+(?:\.\d+)?|\([^()]+\)|pi|e)!(?![=])",
    r"factorial(\1)",
    expression,
)
    expression = expression.replace("^", "**")
    expression = expression.replace("π", "pi")

    expression = re.sub(
    r"(?<![\w.])(\d+(?:\.\d+)?)%",
        r"(\1/100)",
        expression,
    )

    expression = re.sub(
        r"(?<=[0-9.)])(?=(?:pi|e|sqrt|sin|cos|tan|log|ln)\b)",
        "*",
        expression,
    )

    expression = re.sub(
        r"(?<=[0-9)])(?=\()",
        "*",
        expression,
    )

    expression = re.sub(
        r"(?<=\))(?=[0-9a-z])",
        "*",
        expression,
    )

    try:
        tree = ast.parse(expression, mode="eval")
        result = _evaluate(tree.body, degrees)

        if isinstance(result, complex):
            raise ValueError("Complex results are not supported.")

        if not math.isfinite(result):
            raise ValueError("The result is not a finite real number.")

        if isinstance(result, float) and result.is_integer():
            result = int(result)

        return result

    except ZeroDivisionError:
        raise ValueError("You cannot divide by zero.")

    except (SyntaxError, TypeError, OverflowError):
        raise ValueError(
            "Invalid expression. Check the numbers, functions, and operators."
            )


def _evaluate(node, degrees):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Unsupported value.")

    if isinstance(node, ast.Name):
        constants = {
            "pi": math.pi,
            "e": math.e,
        }

        if node.id in constants:
            return constants[node.id]

        raise ValueError("Unknown constant: " + node.id)

    if isinstance(node, ast.UnaryOp):
        value = _evaluate(node.operand, degrees)

        if isinstance(node.op, ast.UAdd):
            return value
        if isinstance(node.op, ast.USub):
            return -value

        raise ValueError("Unsupported unary operator.")

    if isinstance(node, ast.BinOp):
        left = _evaluate(node.left, degrees)
        right = _evaluate(node.right, degrees)

        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            return left / right
        if isinstance(node.op, ast.Pow):
            return left ** right

        raise ValueError("Unsupported math operator.")

    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        function_name = node.func.id

        if len(node.args) != 1 or node.keywords:
            raise ValueError("Enter one argument for this function.")

        value = _evaluate(node.args[0], degrees)

        if function_name == "sqrt":
            if value < 0:
                raise ValueError("Square root of a negative number is not supported.")
            return math.sqrt(value)
        
        if function_name == "log":
            if value <= 0:
                raise ValueError("Logarithm requires a positive number.")
            return math.log10(value)

        if function_name == "ln":
            if value <= 0:
                raise ValueError("Natural logarithm requires a positive number.")
            return math.log(value)

        if function_name in ("sin", "cos", "tan"):
            angle = math.radians(value) if degrees else value

            if function_name == "sin":
                return math.sin(angle)
            if function_name == "cos":
                return math.cos(angle)
            if function_name == "tan":
                if math.isclose(math.cos(angle), 0, abs_tol=1e-12):
                    raise ValueError("Tangent is undefined at this angle.")
            return math.tan(angle)

        raise ValueError("Unsupported function: " + function_name)

    raise ValueError("Invalid mathematical expression.")