from langgraph.graph import StateGraph, END

from .state import ReflectionState
from .nodes import generator_agent, critic_agent


def should_retry(state: ReflectionState):
    if state.get("needs_revision") and state.get("attempts", 0) < 3:
        return "generator"
    return END


def build_graph():
    graph = StateGraph(ReflectionState)

    graph.add_node("generator", generator_agent)
    graph.add_node("critic", critic_agent)

    graph.set_entry_point("generator")
    graph.add_edge("generator", "critic")
    graph.add_conditional_edges("critic", should_retry)

    return graph.compile()