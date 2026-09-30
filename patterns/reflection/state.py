from typing import TypedDict


class ReflectionState(TypedDict):
    task: str
    draft: str
    feedback: str
    final_answer: str
    attempts: int
    needs_revision: bool
    status: str