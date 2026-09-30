from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes import fallback_agent, reasoning_agent, tool_executor


def route_after_reasoning(state: AgentState) -> str:
    return state["intent"]

def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("reasoning_agent", reasoning_agent)
    graph.add_node("math_agent", tool_executor)
    graph.add_node("fallback_agent", fallback_agent)

    graph.set_entry_point("reasoning_agent")
    graph.add_conditional_edges(
        "reasoning_agent",
        route_after_reasoning,
        {"math": "math_agent", "general": "fallback_agent"},
    )
    graph.add_edge("math_agent", END)
    graph.add_edge("fallback_agent", END)

    return graph.compile()
