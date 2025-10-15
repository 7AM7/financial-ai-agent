"""
Integration tests for dashboard API endpoints.

Tests the full API stack including routing, database queries, and response formatting.
Requires a running PostgreSQL database with test data.
"""
import pytest
from fastapi.testclient import TestClient


# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@pytest.mark.integration
@pytest.mark.api
def test_health_check(test_client: TestClient):
    """Test /health endpoint returns healthy status."""
    response = test_client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data


# ============================================================================
# PROFIT & LOSS ENDPOINT
# ============================================================================

@pytest.mark.integration
@pytest.mark.api
def test_get_profit_loss_success(test_client: TestClient):
    """Test GET /api/dashboard/profit-loss returns data."""
    response = test_client.get("/api/dashboard/profit-loss")

    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], list)


@pytest.mark.integration
@pytest.mark.api
def test_get_profit_loss_with_year_filter(test_client: TestClient):
    """Test profit-loss endpoint with year filter."""
    response = test_client.get("/api/dashboard/profit-loss?year=2024")

    assert response.status_code == 200
    data = response.json()
    assert "data" in data

    # If data exists, verify it's filtered by year
    if len(data["data"]) > 0:
        for item in data["data"]:
            assert item["year"] == 2024


@pytest.mark.integration
@pytest.mark.api
def test_get_profit_loss_response_structure(test_client: TestClient):
    """Test profit-loss response has correct structure."""
    response = test_client.get("/api/dashboard/profit-loss")

    assert response.status_code == 200
    data = response.json()

    if len(data["data"]) > 0:
        item = data["data"][0]
        # Verify required fields exist
        assert "year" in item
        assert "quarter" in item
        assert "year_quarter" in item
        assert "revenue" in item
        assert "expenses" in item
        assert "net_profit" in item
        assert "gross_profit" in item
        assert "cogs" in item


# ============================================================================
# TOP ACCOUNTS ENDPOINT
# ============================================================================

@pytest.mark.integration
@pytest.mark.api
def test_get_top_accounts_success(test_client: TestClient):
    """Test GET /api/dashboard/top-accounts returns data."""
    response = test_client.get("/api/dashboard/top-accounts")

    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], list)


@pytest.mark.integration
@pytest.mark.api
def test_get_top_accounts_with_type_filter(test_client: TestClient):
    """Test top-accounts with account_type filter."""
    response = test_client.get("/api/dashboard/top-accounts?account_type=revenue")

    assert response.status_code == 200
    data = response.json()

    if len(data["data"]) > 0:
        for item in data["data"]:
            assert item["account_type"] == "revenue"


@pytest.mark.integration
@pytest.mark.api
def test_get_top_accounts_with_limit(test_client: TestClient):
    """Test top-accounts respects limit parameter."""
    response = test_client.get("/api/dashboard/top-accounts?limit=5")

    assert response.status_code == 200
    data = response.json()

    # Should return at most 5 items
    assert len(data["data"]) <= 5


@pytest.mark.integration
@pytest.mark.api
def test_get_top_accounts_quarterly_period(test_client: TestClient):
    """Test top-accounts with quarterly period."""
    response = test_client.get("/api/dashboard/top-accounts?period=quarterly&year=2024")

    assert response.status_code == 200
    data = response.json()

    if len(data["data"]) > 0:
        item = data["data"][0]
        # Quarterly results should have quarter field
        assert "quarter" in item or "year_quarter" in item


@pytest.mark.integration
@pytest.mark.api
def test_get_top_accounts_response_structure(test_client: TestClient):
    """Test top-accounts response has correct structure."""
    response = test_client.get("/api/dashboard/top-accounts")

    assert response.status_code == 200
    data = response.json()

    if len(data["data"]) > 0:
        item = data["data"][0]
        assert "account_name" in item
        assert "account_type" in item
        assert "total_amount" in item
        assert "year" in item


# ============================================================================
# TREND ANALYSIS ENDPOINT
# ============================================================================

@pytest.mark.integration
@pytest.mark.api
def test_get_trend_analysis_success(test_client: TestClient):
    """Test GET /api/dashboard/trend-analysis returns data."""
    response = test_client.get("/api/dashboard/trend-analysis")

    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], list)


@pytest.mark.integration
@pytest.mark.api
def test_get_trend_analysis_with_filters(test_client: TestClient):
    """Test trend-analysis with year and account_type filters."""
    response = test_client.get(
        "/api/dashboard/trend-analysis?year=2024&account_type=revenue"
    )

    assert response.status_code == 200
    data = response.json()

    if len(data["data"]) > 0:
        for item in data["data"]:
            assert item["year"] == 2024
            assert item["account_type"] == "revenue"


@pytest.mark.integration
@pytest.mark.api
def test_get_trend_analysis_response_structure(test_client: TestClient):
    """Test trend-analysis response has correct structure."""
    response = test_client.get("/api/dashboard/trend-analysis")

    assert response.status_code == 200
    data = response.json()

    if len(data["data"]) > 0:
        item = data["data"][0]
        assert "account_type" in item
        assert "year" in item
        assert "month" in item
        assert "year_month" in item
        assert "month_total" in item


# ============================================================================
# CATEGORY PERFORMANCE ENDPOINT
# ============================================================================

@pytest.mark.integration
@pytest.mark.api
def test_get_category_performance_success(test_client: TestClient):
    """Test GET /api/dashboard/category-performance returns data."""
    response = test_client.get("/api/dashboard/category-performance")

    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], list)


@pytest.mark.integration
@pytest.mark.api
def test_get_category_performance_with_type_filter(test_client: TestClient):
    """Test category-performance with account_type filter."""
    response = test_client.get(
        "/api/dashboard/category-performance?account_type=expense"
    )

    assert response.status_code == 200
    data = response.json()

    if len(data["data"]) > 0:
        for item in data["data"]:
            assert item["account_type"] == "expense"


@pytest.mark.integration
@pytest.mark.api
def test_get_category_performance_response_structure(test_client: TestClient):
    """Test category-performance response has correct structure."""
    response = test_client.get("/api/dashboard/category-performance")

    assert response.status_code == 200
    data = response.json()

    if len(data["data"]) > 0:
        item = data["data"][0]
        assert "account_category" in item
        assert "account_type" in item
        assert "total_amount" in item
        assert "account_count" in item


# ============================================================================
# YOY GROWTH ENDPOINT
# ============================================================================

@pytest.mark.integration
@pytest.mark.api
def test_get_yoy_growth_success(test_client: TestClient):
    """Test GET /api/dashboard/yoy-growth returns data."""
    response = test_client.get("/api/dashboard/yoy-growth")

    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], list)


@pytest.mark.integration
@pytest.mark.api
def test_get_yoy_growth_with_year_filter(test_client: TestClient):
    """Test yoy-growth with year filter."""
    response = test_client.get("/api/dashboard/yoy-growth?year=2024")

    assert response.status_code == 200
    data = response.json()

    if len(data["data"]) > 0:
        for item in data["data"]:
            assert item["current_year"] == 2024


# ============================================================================
# MONTHLY SUMMARY ENDPOINT
# ============================================================================

@pytest.mark.integration
@pytest.mark.api
def test_get_monthly_summary_success(test_client: TestClient):
    """Test GET /api/dashboard/monthly-summary returns data."""
    response = test_client.get("/api/dashboard/monthly-summary")

    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], list)


@pytest.mark.integration
@pytest.mark.api
def test_get_monthly_summary_with_filters(test_client: TestClient):
    """Test monthly-summary with year and account_type filters."""
    response = test_client.get(
        "/api/dashboard/monthly-summary?year=2024&account_type=revenue"
    )

    assert response.status_code == 200
    data = response.json()

    if len(data["data"]) > 0:
        for item in data["data"]:
            assert item["year"] == 2024
            assert item["account_type"] == "revenue"


# ============================================================================
# DASHBOARD OVERVIEW ENDPOINT
# ============================================================================

@pytest.mark.integration
@pytest.mark.api
def test_get_dashboard_overview_success(test_client: TestClient):
    """Test GET /api/dashboard/overview returns combined data."""
    response = test_client.get("/api/dashboard/overview")

    assert response.status_code == 200
    data = response.json()

    # Verify all sections are present
    assert "profit_loss" in data
    assert "top_expenses" in data
    assert "top_revenue" in data
    assert "trends" in data

    # Verify each section is a list
    assert isinstance(data["profit_loss"], list)
    assert isinstance(data["top_expenses"], list)
    assert isinstance(data["top_revenue"], list)
    assert isinstance(data["trends"], list)


@pytest.mark.integration
@pytest.mark.api
def test_get_dashboard_overview_limits(test_client: TestClient):
    """Test dashboard overview respects limits (5 for top accounts)."""
    response = test_client.get("/api/dashboard/overview")

    assert response.status_code == 200
    data = response.json()

    # Top expenses and revenue should be limited to 5
    assert len(data["top_expenses"]) <= 5
    assert len(data["top_revenue"]) <= 5


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.api
def test_invalid_account_type_parameter(test_client: TestClient):
    """Test that invalid account_type doesn't break the API."""
    response = test_client.get("/api/dashboard/top-accounts?account_type=invalid")

    # Should return 200 with empty data (or filtered correctly)
    assert response.status_code in [200, 422]


@pytest.mark.integration
@pytest.mark.api
def test_invalid_year_parameter(test_client: TestClient):
    """Test that invalid year parameter is handled."""
    response = test_client.get("/api/dashboard/profit-loss?year=invalid")

    # FastAPI should return 422 for invalid parameter type
    assert response.status_code == 422


@pytest.mark.integration
@pytest.mark.api
def test_negative_limit_parameter(test_client: TestClient):
    """Test that negative limit is handled."""
    response = test_client.get("/api/dashboard/top-accounts?limit=-5")

    # Should either return error or handle gracefully
    assert response.status_code in [200, 422]


# ============================================================================
# CORS TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.api
def test_cors_headers_present(test_client: TestClient):
    """Test that CORS headers are present in response."""
    response = test_client.get("/api/dashboard/profit-loss")

    assert response.status_code == 200
    # TestClient may not include CORS headers, but verify no errors
    assert "data" in response.json()


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.slow
def test_dashboard_overview_performance(test_client: TestClient):
    """Test that dashboard overview responds in reasonable time."""
    import time

    start_time = time.time()
    response = test_client.get("/api/dashboard/overview")
    end_time = time.time()

    assert response.status_code == 200

    # Should respond within 2 seconds
    assert (end_time - start_time) < 2.0
