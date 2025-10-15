"""
Schema nodes - handle database schema fetching.
"""

from typing_extensions import Literal
from langchain_core.runnables import RunnableConfig
from langgraph.types import Command

from copilotkit.langgraph import copilotkit_customize_config, copilotkit_emit_state

from src.agent.state import FinancialAgentState
from src.agent.sql_utils import get_cached_tables, get_cached_schema, detect_relevant_views


async def list_tables(state: FinancialAgentState, config: RunnableConfig) -> Command[Literal["fetch_schema"]]:
    """List all available tables and views."""
    config = copilotkit_customize_config(
        config,
        emit_intermediate_state=[{"state_key": "status"}]
    )

    updated_state = {**state, "status": "🔍 Analyzing database schema..."}
    await copilotkit_emit_state(config, updated_state)

    tables_text = await get_cached_tables()
    return Command(
        goto="fetch_schema",
        update={"tables": tables_text, "dialect": "PostgreSQL", "top_k": 10, "status": "Analyzing database schema..."}
    )


async def fetch_schema(state: FinancialAgentState, config: RunnableConfig) -> Command[Literal["write_query"]]:
    """Fetch schema for relevant tables only."""
    config = copilotkit_customize_config(
        config,
        emit_intermediate_state=[{"state_key": "status"}]
    )

    updated_state = {**state, "status": "📊 Loading relevant data views..."}
    await copilotkit_emit_state(config, updated_state)

    relevant_views = detect_relevant_views(state["question"])

    try:
        schema_text = await get_cached_schema(relevant_views)
        return Command(goto="write_query", update={"schema": schema_text, "status": "Loading relevant data views..."})
    except Exception as e:
        return Command(
            goto="write_query",
            update={"schema": f"Error: {str(e)}", "query_error": str(e), "status": "Error loading relevant data views..."}
        )
