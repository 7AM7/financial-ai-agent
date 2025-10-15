"""
Helper functions for graph nodes.
"""

from langchain_core.messages import AIMessage


def find_tool_call_id(messages: list) -> str | None:
    """Extract tool_call_id for query_financial_database from message history."""
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and msg.tool_calls:
            for tc in msg.tool_calls:
                if tc.get("name") == "query_financial_database":
                    return tc.get("id")
    return None
