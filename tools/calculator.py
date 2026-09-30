import ast
import math
import operator


_BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

_UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


class _ArithmeticEvaluator(ast.NodeVisitor):
    def visit_Expression(self, node):
        return self.visit(node.body)

    def visit_Constant(self, node):
        if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
            raise ValueError("Only numeric values are allowed.")
        return self._validate_result(node.value)

    def visit_BinOp(self, node):
        operation = _BINARY_OPERATORS.get(type(node.op))
        if operation is None:
            raise ValueError("This arithmetic operator is not supported.")

        left = self.visit(node.left)
        right = self.visit(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 100:
            raise ValueError("Exponents must be between -100 and 100.")

        return self._validate_result(operation(left, right))

    def visit_UnaryOp(self, node):
        operation = _UNARY_OPERATORS.get(type(node.op))
        if operation is None:
            raise ValueError("This unary operator is not supported.")
        return self._validate_result(operation(self.visit(node.operand)))

    def generic_visit(self, node):
        raise ValueError("Only arithmetic expressions are allowed.")

    @staticmethod
    def _validate_result(value):
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError("The result must be finite.")
        if isinstance(value, int) and value.bit_length() > 4096:
            raise ValueError("The result is too large.")
        return value


def calculator(expression: str) -> str:
    try:
        if len(expression) > 500:
            raise ValueError("The expression is too long.")
        tree = ast.parse(expression, mode="eval")
        return str(_ArithmeticEvaluator().visit(tree))
    except (ArithmeticError, SyntaxError, TypeError, ValueError) as error:
        return f"Error: {error}"