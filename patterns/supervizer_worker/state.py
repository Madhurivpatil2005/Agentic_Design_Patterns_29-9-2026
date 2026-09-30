from typing import TypedDict


class SupervisorWorkerState(TypedDict, total=False):
    query: str
    worker: str
    expression: str
    result: str
    employee_name: str
    leave_balance: str