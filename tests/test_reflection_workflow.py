import unittest
from types import SimpleNamespace
from unittest.mock import patch

from patterns.reflection.graph import build_graph
from patterns.reflection.nodes import CriticReview


class ReflectionWorkflowTests(unittest.TestCase):
    @patch("patterns.reflection.nodes.llm")
    def test_python_beginner_example_gets_revised_and_approved(self, llm):
        final_answer = (
            "Python has simple syntax that makes it readable and approachable for beginners. "
            "Its strong community and extensive libraries make learning and building projects easier."
        )
        llm.invoke.return_value = SimpleNamespace(content=final_answer)
        llm.with_structured_output.return_value.invoke.side_effect = [
            CriticReview(needs_revision=False, feedback="Looks good."),
            CriticReview(needs_revision=False, feedback="Looks good."),
        ]

        result = build_graph().invoke(
            {
                "task": "Explain why Python is good for beginners in exactly 2 sentences, mentioning syntax, community, and libraries.",
                "attempts": 0,
                "needs_revision": True,
                "status": "pending",
            }
        )

        self.assertEqual(result["status"], "approved")
        self.assertEqual(result["attempts"], 2)
        self.assertEqual(result["final_answer"], final_answer)

    @patch("patterns.reflection.nodes.llm")
    def test_custom_task_uses_task_specific_review(self, llm):
        draft = "Sunflowers turn toward sunlight as they grow. Mature flower heads later face east."
        llm.invoke.return_value = SimpleNamespace(content=draft)
        llm.with_structured_output.return_value.invoke.return_value = CriticReview(
            needs_revision=False,
            feedback="The answer is concise and relevant.",
        )

        result = build_graph().invoke(
            {
                "task": "Describe two ways sunflowers respond to their environment.",
                "attempts": 0,
                "needs_revision": True,
                "status": "pending",
            }
        )

        self.assertEqual(result["status"], "approved")
        self.assertEqual(result["attempts"], 1)
        self.assertEqual(result["final_answer"], draft)


if __name__ == "__main__":
    unittest.main()