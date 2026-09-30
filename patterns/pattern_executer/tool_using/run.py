from .graph import build_graph

app = build_graph()

result = app.invoke({
    "question": "What is the square of the average of 10 and 5?"
})

print("\n\nResult for Tool-Using Agent:")
print(result)



