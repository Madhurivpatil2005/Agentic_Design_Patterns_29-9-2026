from typing import Literal

from pydantic import BaseModel, Field

from config.llm import get_llm
from tools.calculator import calculator
from .state import AgentState


class ReasoningDecision(BaseModel):
    intent: Literal["math", "general"] = Field(
        description="Use math for arithmetic questions and general for everything else."
    )
    expression: str = Field(
        description="A Python-style arithmetic expression for math, or an empty string for general questions."
    )

def reasoning_agent(state: AgentState):
    prompt = f"""
                You are the reasoning agent in a tool-using workflow.

                Decide whether the question can be answered by evaluating a basic
                arithmetic expression. For arithmetic questions, set intent to
                "math" and convert the requested calculation into an expression
                using only numbers and +, -, *, /, //, %, and **. Do not include
                prose in the expression.

                For all other questions, including definitions, explanations,
                and conversation, set intent to "general" and expression to an
                empty string. Never force a non-arithmetic question into an
                expression.

                Examples:
                Question: What is the sum of 5 and 3?
                Decision: intent=math, expression=5 + 3

                Question: What is the average of 100 and 200?
                Decision: intent=math, expression=(100 + 200) / 2

                Question: What is the square of the average of 100 and 200?
                Decision: intent=math, expression=((100 + 200) / 2) ** 2

                Question: Define AI.
                Decision: intent=general, expression=

                Question: {state['question']}
                Decision:
                """
    decision = get_llm().with_structured_output(ReasoningDecision).invoke(prompt)

    if decision.intent == "math" and not decision.expression.strip():
        raise ValueError("The reasoning agent did not provide an arithmetic expression.")

    return {
        "intent": decision.intent,
        "expression": decision.expression.strip(),
    }

def tool_executor(state: AgentState):
    result = calculator(state["expression"])
    return {"result": result}


def fallback_agent(state: AgentState):
    response = get_llm().invoke(
        [
            (
                "system",
                "You are a helpful assistant. Answer the user's question clearly and directly. "
                "Do not try to turn it into a math expression.",
            ),
            ("human", state["question"]),
        ]
    )
    return {"result": str(response.content).strip()}