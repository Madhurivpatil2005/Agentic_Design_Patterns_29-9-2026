import json

from .graph import build_graph


def run_query(query: str):
    app = build_graph()
    return app.invoke({"query": query})


if __name__ == "__main__":
    for query in [
        "What is the square of the average of 10 and 5?",
        "What is the leave balance for Alice?",
    ]:
        print("Query:", query)
        print(json.dumps(run_query(query), indent=2, ensure_ascii=False))
        print()