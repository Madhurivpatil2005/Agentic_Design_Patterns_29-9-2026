import unittest
from types import SimpleNamespace
from unittest.mock import patch

from patterns.pattern_executer.tool_using.graph import build_graph
from patterns.pattern_executer.tool_using.nodes import ReasoningDecision
from tools.calculator import calculator


class ToolUsingWorkflowTests(unittest.TestCase):
    @patch("patterns.pattern_executer.tool_using.nodes.get_llm")
    def test_arithmetic_question_uses_calculator(self, get_llm):
        llm = get_llm.return_value
        llm.with_structured_output.return_value.invoke.return_value = ReasoningDecision(
            intent="math",
            expression="((10 + 5) / 2) ** 2",
        )

        result = build_graph().invoke(
            {"question": "What is the square of the average of 10 and 5?"}
        )

        self.assertEqual(result["intent"], "math")
        self.assertEqual(result["result"], "56.25")
        llm.invoke.assert_not_called()

    @patch("patterns.pattern_executer.tool_using.nodes.get_llm")
    def test_general_question_uses_fallback_agent(self, get_llm):
        llm = get_llm.return_value
        llm.with_structured_output.return_value.invoke.return_value = ReasoningDecision(
            intent="general",
            expression="",
        )
        llm.invoke.return_value = SimpleNamespace(
            content="Artificial intelligence is the field of building systems that perform tasks associated with human intelligence."
        )

        result = build_graph().invoke({"question": "Define AI."})

        self.assertEqual(result["intent"], "general")
        self.assertIn("Artificial intelligence", result["result"])
        llm.invoke.assert_called_once()


class CalculatorTests(unittest.TestCase):
    def test_evaluates_arithmetic_expression(self):
        self.assertEqual(calculator("((10 + 5) / 2) ** 2"), "56.25")

    def test_rejects_python_code(self):
        result = calculator("__import__('os').system('whoami')")

        self.assertTrue(result.startswith("Error:"))

    def test_rejects_excessive_exponents(self):
        result = calculator("2 ** 101")

        self.assertTrue(result.startswith("Error:"))


if __name__ == "__main__":
    unittest.main()