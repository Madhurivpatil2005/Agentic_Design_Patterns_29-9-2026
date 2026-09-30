from config.llm import get_llm
from tools.calculator import calculator
from tools.leaves_db import get_leave_balance
from .state import SupervisorWorkerState

llm = get_llm()


def supervisor(state: SupervisorWorkerState):
    query = state["query"]

    prompt = f"""
    Decide which worker should handle this request.

    Return ONLY one word:
    - math
    - leave

    Use:
    - math → calculations, percentages, averages, totals
    - leave → leave balance, vacation, sick leave, PTO

    Request: {query}
    """

    worker = llm.invoke(prompt).content.strip().lower()

    if "leave" in worker:
        worker = "leave"
    else:
        worker = "math"

    print(f"[Supervisor] Worker selected: {worker}")

    return {"worker": worker}


def math_agent(state: SupervisorWorkerState):
    query = state["query"]

    prompt = f"""
    Convert this request into a Python arithmetic expression.

    Return only the expression.

    Request: {query}
    """

    expression = llm.invoke(prompt).content.strip()

    print(f"[Math Agent] Expression: {expression}")

    try:
        result = calculator(expression)
    except Exception as e:
        result = f"Error: {e}"

    return {
        "expression": expression,
        "result": result
    }


def leaves_balance(state: SupervisorWorkerState):
    query = state["query"]

    prompt = f"""
    Extract the employee name from this request.

    Return only the employee name.

    Request: {query}
    """

    employee_name = llm.invoke(prompt).content.strip()

    print(f"[Leave Agent] Employee: {employee_name}")

    balance = get_leave_balance(employee_name)

    return {
        "employee_name": employee_name,
        "leave_balance": balance,
        "result": balance
    }