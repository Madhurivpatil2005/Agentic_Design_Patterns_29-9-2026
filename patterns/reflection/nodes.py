from pydantic import BaseModel, Field

from config.llm import get_llm
from .state import ReflectionState

llm = get_llm()


class CriticReview(BaseModel):
    needs_revision: bool = Field(description="Whether the draft needs another revision.")
    feedback: str = Field(description="A concise reason for the review decision.")


def _count_sentences(text: str) -> int:
    cleaned = text.strip()
    if not cleaned:
        return 0
    return len([part for part in cleaned.replace("!", ".").replace("?", ".").split(".") if part.strip()])


def generator_agent(state: ReflectionState):
    previous = state.get("draft", "")
    feedback = state.get("feedback", "")
    attempts = state.get("attempts", 0)
    task = state["task"]
    is_python_beginner_task = "python" in task.lower() and "beginner" in task.lower()

    if attempts == 0 and is_python_beginner_task:
        draft = (
            "Python is a great language for beginners because it is easy to use. "
            "Many people like it and there are many tutorials online."
        )
    else:
        prompt = f"""
        You are the generator agent.
        Write a short answer for the task.

        If feedback is provided, use it to improve the previous answer.
        The answer must satisfy all requirements exactly.
        Keep it concise and direct.

        Task: {task}
        Previous answer: {previous}
        Feedback: {feedback}

        Final answer:
        """
        draft = llm.invoke(prompt).content.strip()

    return {
        "draft": draft,
        "final_answer": draft,
        "attempts": attempts + 1,
        "status": "drafted",
    }


def critic_agent(state: ReflectionState):
    task = state["task"]
    prompt = f"""
    You are the critic agent.
    Review this answer strictly.

    Rules:
    - The answer must directly answer the task.
    - It must be concise and clear.
    - It must not be vague or generic.
    - If the task requires exact structure, follow it exactly.
    - Do not approve weak answers.

    Return ONLY valid JSON in this exact shape:
    {{"needs_revision": true, "feedback": "short reason"}}

    Task: {task}
    Answer: {state['draft']}
    """

    review = llm.with_structured_output(CriticReview).invoke(prompt)
    print(f"[Critic Agent] LLM response: {review.model_dump()}")

    needs_revision = review.needs_revision
    feedback = review.feedback.strip() or "Looks good."

    text = state.get("draft", "")
    sentence_count = _count_sentences(text)
    lower_text = text.lower()
    lower_task = task.lower()
    is_python_beginner_task = "python" in lower_task and "beginner" in lower_task
    requires_two_sentences = (
        "exactly 2 sentences" in lower_task or "exactly two sentences" in lower_task
    )

    if requires_two_sentences and sentence_count != 2:
        needs_revision = True
        feedback = "Answer must be exactly 2 sentences."
    elif is_python_beginner_task and all(
        term not in lower_text for term in ("syntax", "readable", "simple")
    ):
        needs_revision = True
        feedback = "Answer should mention why Python is beginner-friendly." \
            " Include simplicity/readability or easy syntax."
    elif is_python_beginner_task and all(
        term not in lower_text for term in ("community", "library", "libraries")
    ):
        needs_revision = True
        feedback = "Answer should mention community, libraries, or available resources."

    if not needs_revision:
        return {
            "needs_revision": False,
            "feedback": "Looks good.",
            "status": "approved",
            "final_answer": state["draft"],
        }

    return {
        "needs_revision": True,
        "feedback": feedback,
        "status": "needs_improvement",
        "attempts": state.get("attempts", 0),
    }