"""
SQL nodes - handle SQL query generation, validation, execution, and repair.
"""
import json
import logging
from typing_extensions import Literal
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langgraph.types import Command

from copilotkit.langgraph import copilotkit_customize_config, copilotkit_emit_state

from src.agent.state import FinancialAgentState
from src.agent.prompts import WRITE_PROMPT, CHECK_PROMPT, REPAIR_PROMPT
from src.agent.sql_utils import writer, checker, is_simple_query, query_tool
from src.agent.nodes.helpers import find_tool_call_id

logger = logging.getLogger(__name__)



async def write_query(state: FinancialAgentState, config: RunnableConfig) -> Command[Literal["check_query", "exec_query", "chat_node"]]:
    """Generate a SQL query from the question."""
    config = copilotkit_customize_config(
        config,
        emit_intermediate_state=[{"state_key": "status"}]
    )

    question = state.get("question", "").strip()
    if not question:
        tool_call_id = find_tool_call_id(state["messages"])
        error_content = "No question provided for SQL generation"
        tool_message = ToolMessage(content=error_content, tool_call_id=tool_call_id) if tool_call_id else AIMessage(content=error_content)

        return Command(
            goto="chat_node",
            update={"messages": [tool_message], "status": "No question provided for SQL generation"}
        )

    updated_state = {**state, "status": "✍️ Writing SQL query..."}
    await copilotkit_emit_state(config, updated_state)

    try:
        chain = WRITE_PROMPT | writer
        result = await chain.ainvoke({
            "top_k": state.get("top_k", 10),
            "question": state["question"],
            "tables": state.get("tables", ""),
            "schema": state.get("schema", "")
        })
        sql_query = result.query
        logger.info(f"[DEBUG] Written query: {sql_query}")

        updated_state = {**state, "status": "Query generated..."}
        await copilotkit_emit_state(config, updated_state)

        if is_simple_query(sql_query):
            return Command(goto="exec_query", update={"sql": sql_query, "status": "Query generated"})
        else:
            return Command(goto="check_query", update={"sql": sql_query, "status": "Query generated"})
    except Exception as e:
        tool_call_id = find_tool_call_id(state["messages"])
        error_content = f"Error generating query: {str(e)}"
        tool_message = ToolMessage(content=error_content, tool_call_id=tool_call_id) if tool_call_id else AIMessage(content=error_content)

        return Command(
            goto="chat_node",
            update={"messages": [tool_message], "status": "❌ Query generation failed"}
        )


async def check_query(state: FinancialAgentState, config: RunnableConfig) -> Command[Literal["exec_query"]]:
    """Check the SQL for mistakes and possibly rewrite it."""
    config = copilotkit_customize_config(
        config,
        emit_intermediate_state=[{"state_key": "status"}]
    )

    updated_state = {**state, "status": "🔍 Validating query..."}
    await copilotkit_emit_state(config, updated_state)
    logger.info(f"[DEBUG] Checking query: {state['sql']}")

    try:
        chain = CHECK_PROMPT | checker
        result = await chain.ainvoke({"sql": state["sql"]})
        sql_query = result.query
        updated_state = {**state, "status": "Query validated"}
        await copilotkit_emit_state(config, updated_state)

        return Command(goto="exec_query", update={"checked_sql": sql_query, "status": "Query validated"})
    except Exception:
        return Command(goto="exec_query", update={"checked_sql": state["sql"], "status": "Query failed to validate"})


async def exec_query(state: FinancialAgentState, config: RunnableConfig) -> Command[Literal["repair_query", "chat_node"]]:
    """Execute the SQL (wrapped to JSON) and capture structured results."""
    config = copilotkit_customize_config(
        config,
        emit_intermediate_state=[
            {"state_key": "status"},
            {"state_key": "sql"},
            {"state_key": "result_data"},
            {"state_key": "result_columns"},
            {"state_key": "result_count"},
        ]
    )

    updated_state = {**state, "status": "⚡ Executing query..."}
    await copilotkit_emit_state(config, updated_state)

    sql = state.get("checked_sql") or state["sql"]
    logger.info(f"[DEBUG] Executing query... {state.get('checked_sql')}")
    tool_call_id = find_tool_call_id(state["messages"])
    try:
        result = await query_tool.arun({"query": sql})
        content = getattr(result, "content", result)
        logger.info(f"[DEBUG] Executed query result: {content}")
        content_str = json.dumps(content) if content else "[]"

        updated_state_with_results = {
            **state,
            "result": content_str,                 
            "sql": sql,                     
            "status": "✅ Query completed"
        }
        await copilotkit_emit_state(config, updated_state_with_results)
        
        tool_message = ToolMessage(content=content_str, tool_call_id=tool_call_id) if tool_call_id else AIMessage(content=content_str)
        return Command(
            goto="chat_node",
            update={
                "messages": [tool_message],
                "status": "✅ Query completed",
                "sql": sql,
                "result": content_str
            }
        )

    except Exception as e:
        error_msg = str(e)
        retries = state.get("retries", 0)

        if retries < 2:
            return Command(
                goto="repair_query",
                update={
                    "query_error": error_msg,
                    "retries": retries + 1,
                    "checked_sql": sql,
                    "status": "❌ Query failed"
                }
            )
        else:
            error_content = f"Error querying the database: {error_msg}"
            tool_message = ToolMessage(content=error_content, tool_call_id=tool_call_id) if tool_call_id else AIMessage(content=error_content)
            return Command(
                goto="chat_node",
                update={"messages": [tool_message], "status": "Query failed to execute"}
            )


async def repair_query(state: FinancialAgentState, config: RunnableConfig) -> Command[Literal["exec_query"]]:
    """Repair SQL based on execution error."""
    config = copilotkit_customize_config(
        config,
        emit_intermediate_state=[{"state_key": "status"}]
    )

    updated_state = {**state, "status": "🔧 Fixing query..."}
    await copilotkit_emit_state(config, updated_state)

    try:
        chain = REPAIR_PROMPT | checker
        result = await chain.ainvoke({
            "error": state.get("query_error", ""),
            "sql": state.get("checked_sql") or state["sql"]
        })

        sql_query = result.query
        updated_state = {**state, "status": "Query repaired"}
        await copilotkit_emit_state(config, updated_state)

        return Command(goto="exec_query", update={"checked_sql": sql_query, "query_error": "", "status": "Query repaired"})
    except Exception:
        return Command(goto="exec_query", update={"status": "Query failed to repair"})
