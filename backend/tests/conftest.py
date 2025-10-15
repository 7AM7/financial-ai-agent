"""
Pytest configuration and shared fixtures for backend tests.
"""
import os
import pytest
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from src.main import app
from src.config import BackendSettings
from src.db import get_db


# ============================================================================
# TEST CONFIGURATION
# ============================================================================

@pytest.fixture(scope="session")
def test_settings():
    """Override settings for testing."""
    return BackendSettings(
        postgres_host="localhost",
        postgres_port=5432,
        postgres_db="financial_data_test",
        postgres_user="postgres",
        postgres_password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        # Mock LLM settings (tests should mock LLM calls)
        model="gpt-4o-mini",
        model_provider="azure_openai",
        api_key="test-api-key",
        azure_endpoint="https://test.openai.azure.com/",
        azure_deployment="gpt-4o-mini",
    )


# ============================================================================
# DATABASE FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def test_db_engine(test_settings):
    """
    Create a test database engine.

    Note: Uses the actual PostgreSQL test database.
    For faster unit tests, individual tests can use in-memory SQLite.
    """
    engine = create_engine(
        test_settings.postgres_url,
        poolclass=StaticPool,  # Use static pool for testing
        echo=False,
    )
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def test_db_session(test_db_engine) -> Generator[Session, None, None]:
    """
    Create a test database session.

    Each test gets a fresh session with automatic rollback.
    """
    SessionLocal = sessionmaker(bind=test_db_engine)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def override_get_db(test_db_session):
    """Override the get_db dependency for FastAPI tests."""
    def _override_get_db():
        try:
            yield test_db_session
        finally:
            pass
    return _override_get_db


# ============================================================================
# API CLIENT FIXTURES
# ============================================================================

@pytest.fixture(scope="function")
def test_client(override_get_db) -> TestClient:
    """
    Create a FastAPI test client with database dependency override.
    """
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


# ============================================================================
# MOCK LLM FIXTURES
# ============================================================================

@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing agent workflows."""
    return {
        "query": "SELECT * FROM v_ai_financial_data LIMIT 10",
        "reasoning": "Simple query to fetch financial data",
    }


@pytest.fixture
def mock_llm(mocker, mock_llm_response):
    """Mock LangChain LLM calls to avoid API costs."""
    mock = mocker.patch("src.agent.sql_utils.writer")
    mock.ainvoke = mocker.AsyncMock(return_value=type('obj', (object,), mock_llm_response))
    return mock


# ============================================================================
# SAMPLE DATA FIXTURES
# ============================================================================

@pytest.fixture
def sample_profit_loss_data():
    """Sample profit & loss data for testing."""
    return [
        {
            "year": 2024,
            "quarter": 1,
            "year_quarter": "2024-Q1",
            "revenue": 5200000.0,
            "cogs": 2100000.0,
            "expenses": 1900000.0,
            "gross_profit": 3100000.0,
            "net_profit": 1200000.0,
            "profit_margin_percent": 23.08,
        },
        {
            "year": 2024,
            "quarter": 2,
            "year_quarter": "2024-Q2",
            "revenue": 5800000.0,
            "cogs": 2300000.0,
            "expenses": 2000000.0,
            "gross_profit": 3500000.0,
            "net_profit": 1500000.0,
            "profit_margin_percent": 25.86,
        },
    ]


@pytest.fixture
def sample_top_accounts_data():
    """Sample top accounts data for testing."""
    return [
        {
            "account_name": "Product Sales",
            "account_type": "revenue",
            "account_category": "Sales Revenue",
            "year": 2024,
            "transaction_count": 1200,
            "total_amount": 3200000.0,
            "avg_amount": 2666.67,
            "rank_in_type_year": 1,
        },
        {
            "account_name": "Salaries and Wages",
            "account_type": "expense",
            "account_category": "Payroll & Compensation",
            "year": 2024,
            "transaction_count": 850,
            "total_amount": 1250000.0,
            "avg_amount": 1470.59,
            "rank_in_type_year": 1,
        },
    ]


# ============================================================================
# AGENT STATE FIXTURES
# ============================================================================

@pytest.fixture
def sample_agent_state():
    """Sample LangGraph agent state for testing."""
    return {
        "messages": [],
        "question": "What was total revenue in Q1 2024?",
        "dialect": "PostgreSQL",
        "top_k": 10,
        "tables": "v_ai_financial_data, v_profit_loss",
        "schema": "Columns: year, quarter, revenue, expenses...",
        "sql": "",
        "checked_sql": "",
        "result": "",
        "result_data": [],
        "result_columns": [],
        "result_count": 0,
        "query_error": "",
        "retries": 0,
        "status": "thinking...",
    }


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests (fast, isolated)")
    config.addinivalue_line("markers", "integration: Integration tests (require database)")
    config.addinivalue_line("markers", "slow: Slow tests (> 1 second)")
    config.addinivalue_line("markers", "agent: LangGraph agent workflow tests")
    config.addinivalue_line("markers", "api: API endpoint tests")
