import json

from .graph import build_graph


def run_query(task: str):
    app = build_graph()
    return app.invoke({
        "task": task,
        "attempts": 0,
        "needs_revision": True,
        "status": "pending",
    })


if __name__ == "__main__":
    task = (
        "Explain why Python is a good language for beginners in exactly 2 sentences. "
        "Mention simple syntax, strong community support, and the availability of libraries. "
        "Do not use fluff or extra paragraphs."
    )
    result = run_query(task)
    print(json.dumps(result, indent=2, ensure_ascii=False))