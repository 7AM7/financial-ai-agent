"""
Agent routes for CopilotKit integration.
"""

from fastapi import APIRouter
from ag_ui_langgraph import add_langgraph_fastapi_endpoint
from copilotkit import CopilotKitRemoteEndpoint, LangGraphAGUIAgent

from src.agent import graph


router = APIRouter()
sdk = CopilotKitRemoteEndpoint(
    agents=[
        LangGraphAGUIAgent(
            name="financial_assistant",
            description="Financial AI Assistant specialized in analyzing QuickBooks and Rootfi data. "
            "Provides conversational support, explains financial concepts, and queries the database "
            "for specific metrics, trends, and insights. Can handle both general questions and "
            "data-driven analysis.",
            graph=graph,
        )
    ],
)


def register_copilotkit_endpoint(app):
    """Register the CopilotKit endpoint with the FastAPI app."""
    add_langgraph_fastapi_endpoint(
        app=app,
        agent=LangGraphAGUIAgent(
            name="financial_assistant",
            description="Financial AI Assistant specialized in analyzing QuickBooks and Rootfi data. "
            "Provides conversational support, explains financial concepts, and queries the database "
            "for specific metrics, trends, and insights. Can handle both general questions and "
            "data-driven analysis.",
            graph=graph,
        ),
        path="/copilotkit/agents/financial_assistant"
    )