"""
Chat node - main entry point for the agent workflow.
"""

from typing_extensions import Literal
from langchain_core.messages import SystemMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.types import Command
from langgraph.graph import END

from copilotkit.langgraph import copilotkit_emit_state, copilotkit_customize_config

from src.llm.provider_manager import get_llm
from src.agent.state import FinancialAgentState
from src.agent.tools import query_financial_database
from src.agent.prompts import SYSTEM_PROMPT


async def chat_node(state: FinancialAgentState, config: RunnableConfig) -> Command[Literal["list_tables", "__end__"]]:
    """
    Main chat node - decides if we need to query data or just respond.
    """
    config = copilotkit_customize_config(
        config,
        emit_intermediate_state=
        [
            {
                "state_key": "status",
                "tool": "query_financial_database",
                "tool_argument": "question",
            }
        ]
    )

    model = get_llm()

    all_tools = [
        *state["copilotkit"]["actions"],
        query_financial_database,
    ]
    model_with_tools = model.bind_tools(
        all_tools,
        parallel_tool_calls=False
    )

    system_message = SystemMessage(content=SYSTEM_PROMPT)
    response = await model_with_tools.ainvoke(
        [system_message, *state["messages"]],
        config
    )

    if isinstance(response, AIMessage) and response.tool_calls:
        tool_call = response.tool_calls[0]

        if tool_call.get("name") == "query_financial_database":
            question = tool_call.get("args", {}).get("question", "")
            updated_state = {**state, "status": "Analyzing your query..."}
            await copilotkit_emit_state(config, updated_state)
            return Command(
                goto="list_tables",
                update={
                    "messages": [response],
                    "question": question,
                    "checked_sql": "",
                    "status": "Analyzing your query..."
                }
            )

    return Command(goto=END, update={"messages": response, "status": "Response generated"})
