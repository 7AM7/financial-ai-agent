"""
Agent state definition for the Financial AI Agent.
"""

from langgraph.graph import MessagesState
from copilotkit import CopilotKitState


class FinancialAgentState(CopilotKitState):
    """
    Unified agent state extending MessagesState.

    Combines conversational state with SQL query execution state.
    """
    status: str = "thinking..."

    # SQL query fields
    question: str = ""
    dialect: str = "PostgreSQL"
    top_k: int = 10
    tables: str = ""
    schema: str = ""
    sql: str = ""
    result: str = ""
    query_error: str = ""
    retries: int = 0

    # Structured result fields for generative UI
    result_data: list[dict] = []
    result_columns: list[str] = []
    result_count: int = 0
    checked_sql: str = ""