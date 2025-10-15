"""
SQL utility functions for query generation and validation.
"""
from decimal import Decimal
from typing import Any
import re
from pydantic import BaseModel, Field
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from src.llm.provider_manager import get_llm
from src.db import get_langchain_db


# ============================================================================
# DATABASE SETUP
# ============================================================================

# Initialize LLM and database
llm = get_llm()

db = get_langchain_db()
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
tools = {tool.name: tool for tool in toolkit.get_tools()}

# SQL database tools
list_tables_tool = tools["sql_db_list_tables"]
schema_tool = tools["sql_db_schema"]
query_tool = tools["sql_db_query"]


# ============================================================================
# SQL STRUCTURED OUTPUT
# ============================================================================

class SQLDraft(BaseModel):
    """Pydantic class for SQL output."""
    query: str = Field(description="A valid PostgreSQL SELECT query. Only use LIMIT when explicitly asking for top/most/first N results.")
    explanation: str = Field(description="Brief explanation of what the query does", default="")


writer = llm.with_structured_output(SQLDraft)
checker = llm.with_structured_output(SQLDraft)

# Schema cache
_SCHEMA_CACHE: dict[str, str] = {}
_TABLES_CACHE: str = ""


# ============================================================================
# CACHE FUNCTIONS
# ============================================================================

async def get_cached_schema(table_names: str) -> str:
    """Get schema from cache or fetch and cache it."""
    if table_names not in _SCHEMA_CACHE:
        result = await schema_tool.arun({"table_names": table_names})
        _SCHEMA_CACHE[table_names] = getattr(result, "content", result)
    return _SCHEMA_CACHE[table_names]


async def get_cached_tables() -> str:
    """Get tables list from cache or fetch and cache it."""
    global _TABLES_CACHE
    if not _TABLES_CACHE:
        result = await list_tables_tool.arun({})
        _TABLES_CACHE = getattr(result, "content", result)
    return _TABLES_CACHE


# ============================================================================
# VIEW DETECTION
# ============================================================================

def detect_relevant_views(question: str) -> str:
    """Detect which views are relevant based on question keywords."""
    question_lower = question.lower()
    views = ["v_ai_financial_data"]

    if any(word in question_lower for word in ["profit", "loss", "p&l", "margin", "net profit"]):
        views.append("v_profit_loss")
    if any(word in question_lower for word in ["trend", "month over month", "mom", "monthly change"]):
        views.append("v_trend_analysis")
    if any(word in question_lower for word in ["year over year", "yoy", "growth", "compare years"]):
        views.append("v_yoy_growth")
    if any(word in question_lower for word in ["category", "categories", "by category"]):
        views.append("v_category_performance")
    if any(word in question_lower for word in ["top accounts", "highest", "largest accounts"]):
        if any(word in question_lower for word in ["quarter", "q1", "q2", "q3", "q4"]):
            views.append("v_top_accounts_quarterly")
        else:
            views.append("v_top_accounts_yearly")

    return ", ".join(views)


# ============================================================================
# SQL QUERY ANALYSIS
# ============================================================================

def is_simple_query(sql: str) -> bool:
    """Determine if a query is simple enough to skip validation."""
    sql_lower = sql.lower()
    complex_indicators = [
        r"\bjoin\b", r"\bunion\b", r"\bwith\b",
        r"\bcase\s+when\b", r"group\s+by\s+.*having"
    ]

    if re.search(r"\(\s*select", sql_lower):
        return False
    if len(re.findall(r"\bfrom\b", sql_lower)) > 1:
        return False
    if any(re.search(pattern, sql_lower) for pattern in complex_indicators):
        return False

    return True
