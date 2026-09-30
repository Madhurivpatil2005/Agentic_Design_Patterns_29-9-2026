from typing import Literal, TypedDict


class AgentState(TypedDict, total=False):
    question: str
    intent: Literal["math", "general"]
    expression: str
    result: str