"""
LangGraph workflow construction for the Financial AI Agent.
"""

from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver

from src.agent.state import FinancialAgentState
from src.agent.nodes import (
    chat_node,
    list_tables,
    fetch_schema,
    write_query,
    check_query,
    exec_query,
    repair_query,
)


def build_agent_graph():
    """
    Build and compile the Financial AI Agent graph.

    Returns:
        Compiled LangGraph workflow
    """
    workflow = StateGraph(FinancialAgentState)

    # Add all nodes
    workflow.add_node("chat_node", chat_node)
    workflow.add_node("list_tables", list_tables)
    workflow.add_node("fetch_schema", fetch_schema)
    workflow.add_node("write_query", write_query)
    workflow.add_node("check_query", check_query)
    workflow.add_node("exec_query", exec_query)
    workflow.add_node("repair_query", repair_query)

    # Set entry point
    workflow.set_entry_point("chat_node")

    # Compile with memory
    memory = MemorySaver()
    graph = workflow.compile(checkpointer=memory)

    return graph


# Export the compiled graph
graph = build_agent_graph()
