"""
Tool definitions for the Financial AI Agent.
"""

from langchain.tools import tool


@tool
def query_financial_database(question: str):
    """
    Query the financial database using natural language.

    Use this tool when the user asks questions that require actual data from the database.

    Examples of when to use this tool:
    - "What was revenue in Q1 2024?"
    - "Show me top 5 expense accounts"
    - "What is the profit margin trend?"
    - "Compare revenue year-over-year"
    - Any question requiring specific numbers, accounts, dates, or financial metrics

    Args:
        question: Natural language question about financial data

    Returns:
        Answer with financial data, metrics, and insights
    """