import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "employee_leaves.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_db() -> None:
    conn = get_connection()
    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS leave_balances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_name TEXT UNIQUE NOT NULL,
                leave_balance INTEGER NOT NULL
            )
            """
        )
        row = conn.execute("SELECT COUNT(*) AS count FROM leave_balances").fetchone()
        if row is None or row["count"] == 0:
            conn.executemany(
                "INSERT INTO leave_balances (employee_name, leave_balance) VALUES (?, ?)",
                [
                    ("Alice", 12),
                    ("Bob", 5),
                    ("Charlie", 18),
                ],
            )
    conn.close()


def get_leave_balance(employee_name: str) -> str:
    initialize_db()
    conn = get_connection()
    try:
        cursor = conn.execute(
            "SELECT leave_balance FROM leave_balances WHERE LOWER(employee_name) = LOWER(?)",
            (employee_name.strip(),),
        )
        row = cursor.fetchone()
        if row is None:
            return f"No leave balance record found for '{employee_name}'."
        return f"{employee_name.title()} has {row['leave_balance']} leave days remaining."
    finally:
        conn.close()