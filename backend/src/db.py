"""
Database connection for FastAPI backend.
Uses SQLAlchemy and LangChain SQLDatabase for SQL agent.
"""
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from langchain_community.utilities import SQLDatabase

from src.config import settings


# Create SQLAlchemy engine
engine = create_engine(
    settings.postgres_url,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database sessions.

    Usage:
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_langchain_db() -> SQLDatabase:
    """
    Get LangChain SQLDatabase for SQL agent.

    This provides tools for:
    - sql_db_list_tables: List available tables
    - sql_db_schema: Get table schemas
    - sql_db_query: Execute SQL queries
    """
    return SQLDatabase.from_uri(
        settings.postgres_url,
        include_tables=[
            "v_ai_financial_data",
            "dim_account",
            "dim_date",
            "dim_source",
            "fact_financials",
            "v_monthly_summary",
            "v_category_performance",
            "v_profit_loss",
            "v_yoy_growth",
            "v_top_accounts_yearly",
            "v_top_accounts_quarterly",
            "v_trend_analysis",
        ],
        sample_rows_in_table_info=3,
        view_support=True
    )
