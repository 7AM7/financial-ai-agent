"""
Unit tests for analytics service functions.

Tests the analytics service layer without requiring a real database.
Uses mocked database responses to test data transformation logic.
"""
import pytest
from unittest.mock import MagicMock, call
from sqlalchemy import text

from src.services.analytics_service import (
    get_monthly_summary,
    get_category_performance,
    get_profit_loss,
    get_yoy_growth,
    get_top_accounts,
    get_trend_analysis,
)


# ============================================================================
# UNIT TESTS - get_profit_loss()
# ============================================================================

@pytest.mark.unit
def test_get_profit_loss_no_filters(mocker):
    """Test get_profit_loss without filters."""
    # Mock database session
    mock_db = MagicMock()
    mock_result = MagicMock()

    # Mock data returned from database
    mock_rows = [
        MagicMock(
            year=2024,
            quarter=1,
            year_quarter="2024-Q1",
            revenue=5200000.0,
            cogs=2100000.0,
            expenses=1900000.0,
            gross_profit=3100000.0,
            net_profit=1200000.0,
            profit_margin_percent=23.08,
        ),
        MagicMock(
            year=2024,
            quarter=2,
            year_quarter="2024-Q2",
            revenue=5800000.0,
            cogs=2300000.0,
            expenses=2000000.0,
            gross_profit=3500000.0,
            net_profit=1500000.0,
            profit_margin_percent=25.86,
        ),
    ]

    mock_result.__iter__ = lambda self: iter(mock_rows)
    mock_db.execute.return_value = mock_result

    # Call function
    result = get_profit_loss(mock_db, year=None)

    # Assertions
    assert len(result) == 2
    assert result[0].year == 2024
    assert result[0].quarter == 1
    assert result[0].revenue == 5200000.0
    assert result[0].net_profit == 1200000.0
    assert result[1].year_quarter == "2024-Q2"

    # Verify SQL was called correctly
    mock_db.execute.assert_called_once()
    call_args = mock_db.execute.call_args
    assert "v_profit_loss" in call_args[0][0].text


@pytest.mark.unit
def test_get_profit_loss_with_year_filter(mocker):
    """Test get_profit_loss with year filter."""
    mock_db = MagicMock()
    mock_result = MagicMock()

    mock_rows = [
        MagicMock(
            year=2024,
            quarter=1,
            year_quarter="2024-Q1",
            revenue=5200000.0,
            cogs=2100000.0,
            expenses=1900000.0,
            gross_profit=3100000.0,
            net_profit=1200000.0,
            profit_margin_percent=23.08,
        ),
    ]

    mock_result.__iter__ = lambda self: iter(mock_rows)
    mock_db.execute.return_value = mock_result

    # Call with year filter
    result = get_profit_loss(mock_db, year=2024)

    # Assertions
    assert len(result) == 1
    assert result[0].year == 2024

    # Verify year parameter was passed
    call_args = mock_db.execute.call_args
    assert call_args[1] == {"year": 2024}


@pytest.mark.unit
def test_get_profit_loss_handles_null_margin():
    """Test that null profit_margin_percent is handled correctly."""
    mock_db = MagicMock()
    mock_result = MagicMock()

    mock_rows = [
        MagicMock(
            year=2024,
            quarter=1,
            year_quarter="2024-Q1",
            revenue=0.0,
            cogs=0.0,
            expenses=0.0,
            gross_profit=0.0,
            net_profit=0.0,
            profit_margin_percent=None,  # ← null value
        ),
    ]

    mock_result.__iter__ = lambda self: iter(mock_rows)
    mock_db.execute.return_value = mock_result

    result = get_profit_loss(mock_db)

    assert len(result) == 1
    assert result[0].profit_margin_percent is None


# ============================================================================
# UNIT TESTS - get_top_accounts()
# ============================================================================

@pytest.mark.unit
def test_get_top_accounts_yearly_default():
    """Test get_top_accounts with default yearly period."""
    mock_db = MagicMock()
    mock_result = MagicMock()

    mock_rows = [
        MagicMock(
            account_name="Product Sales",
            account_type="revenue",
            account_category="Sales Revenue",
            year=2024,
            transaction_count=1200,
            total_amount=3200000.0,
            avg_amount=2666.67,
            rank_in_type_year=1,
        ),
    ]

    mock_result.__iter__ = lambda self: iter(mock_rows)
    mock_db.execute.return_value = mock_result

    result = get_top_accounts(mock_db, account_type="revenue", year=2024, limit=10)

    assert len(result) == 1
    assert result[0].account_name == "Product Sales"
    assert result[0].rank_in_type_year == 1

    # Verify correct view was used
    call_args = mock_db.execute.call_args
    assert "v_top_accounts_yearly" in call_args[0][0].text


@pytest.mark.unit
def test_get_top_accounts_quarterly():
    """Test get_top_accounts with quarterly period."""
    mock_db = MagicMock()
    mock_result = MagicMock()

    mock_rows = [
        MagicMock(
            account_name="Salaries",
            account_type="expense",
            account_category="Payroll",
            year=2024,
            quarter=1,
            year_quarter="2024-Q1",
            transaction_count=250,
            total_amount=320000.0,
            avg_amount=1280.0,
            rank_in_quarter=1,
        ),
    ]

    mock_result.__iter__ = lambda self: iter(mock_rows)
    mock_db.execute.return_value = mock_result

    result = get_top_accounts(
        mock_db,
        account_type="expense",
        year=2024,
        period="quarterly",
        limit=5
    )

    assert len(result) == 1
    assert result[0].account_name == "Salaries"
    assert result[0].year_quarter == "2024-Q1"
    assert result[0].rank_in_quarter == 1

    # Verify quarterly view was used
    call_args = mock_db.execute.call_args
    assert "v_top_accounts_quarterly" in call_args[0][0].text


# ============================================================================
# UNIT TESTS - get_trend_analysis()
# ============================================================================

@pytest.mark.unit
def test_get_trend_analysis_with_filters():
    """Test get_trend_analysis with year and account_type filters."""
    mock_db = MagicMock()
    mock_result = MagicMock()

    mock_rows = [
        MagicMock(
            account_type="revenue",
            year=2024,
            month=3,
            year_month="2024-03",
            month_total=1800000.0,
            prev_month_total=1650000.0,
            mom_change=150000.0,
            mom_change_percent=9.09,
        ),
        MagicMock(
            account_type="revenue",
            year=2024,
            month=2,
            year_month="2024-02",
            month_total=1650000.0,
            prev_month_total=1500000.0,
            mom_change=150000.0,
            mom_change_percent=10.0,
        ),
    ]

    mock_result.__iter__ = lambda self: iter(mock_rows)
    mock_db.execute.return_value = mock_result

    result = get_trend_analysis(mock_db, year=2024, account_type="revenue")

    assert len(result) == 2
    assert result[0].month_total == 1800000.0
    assert result[0].mom_change_percent == 9.09
    assert result[1].year_month == "2024-02"

    # Verify filters were applied
    call_args = mock_db.execute.call_args
    assert call_args[1] == {"year": 2024, "account_type": "revenue"}


@pytest.mark.unit
def test_get_trend_analysis_handles_nulls():
    """Test that null prev_month values are handled correctly."""
    mock_db = MagicMock()
    mock_result = MagicMock()

    mock_rows = [
        MagicMock(
            account_type="revenue",
            year=2024,
            month=1,
            year_month="2024-01",
            month_total=1500000.0,
            prev_month_total=None,  # ← First month has no previous
            mom_change=None,
            mom_change_percent=None,
        ),
    ]

    mock_result.__iter__ = lambda self: iter(mock_rows)
    mock_db.execute.return_value = mock_result

    result = get_trend_analysis(mock_db, year=2024)

    assert len(result) == 1
    assert result[0].prev_month_total is None
    assert result[0].mom_change is None
    assert result[0].mom_change_percent is None


# ============================================================================
# UNIT TESTS - get_category_performance()
# ============================================================================

@pytest.mark.unit
def test_get_category_performance_no_filter():
    """Test get_category_performance without filters."""
    mock_db = MagicMock()
    mock_result = MagicMock()

    mock_rows = [
        MagicMock(
            account_category="Payroll & Compensation",
            account_type="expense",
            year=2024,
            quarter=1,
            year_quarter="2024-Q1",
            account_count=15,
            transaction_count=850,
            total_amount=1250000.0,
            avg_amount=1470.59,
            min_amount=50000.0,
            max_amount=120000.0,
        ),
    ]

    mock_result.__iter__ = lambda self: iter(mock_rows)
    mock_db.execute.return_value = mock_result

    result = get_category_performance(mock_db)

    assert len(result) == 1
    assert result[0].account_category == "Payroll & Compensation"
    assert result[0].total_amount == 1250000.0
    assert result[0].account_count == 15


@pytest.mark.unit
def test_get_category_performance_with_type_filter():
    """Test get_category_performance with account_type filter."""
    mock_db = MagicMock()
    mock_result = MagicMock()

    mock_rows = [
        MagicMock(
            account_category="Sales Revenue",
            account_type="revenue",
            year=2024,
            quarter=1,
            year_quarter="2024-Q1",
            account_count=8,
            transaction_count=1200,
            total_amount=3200000.0,
            avg_amount=2666.67,
            min_amount=100000.0,
            max_amount=500000.0,
        ),
    ]

    mock_result.__iter__ = lambda self: iter(mock_rows)
    mock_db.execute.return_value = mock_result

    result = get_category_performance(mock_db, account_type="revenue")

    assert len(result) == 1
    assert result[0].account_type == "revenue"

    # Verify filter was applied
    call_args = mock_db.execute.call_args
    assert call_args[1] == {"account_type": "revenue"}


# ============================================================================
# UNIT TESTS - get_yoy_growth()
# ============================================================================

@pytest.mark.unit
def test_get_yoy_growth_with_year_filter():
    """Test get_yoy_growth with year filter."""
    mock_db = MagicMock()
    mock_result = MagicMock()

    mock_rows = [
        MagicMock(
            account_category="Sales Revenue",
            account_type="revenue",
            current_year=2024,
            current_amount=3200000.0,
            previous_amount=2800000.0,
            absolute_growth=400000.0,
            growth_percent=14.29,
        ),
    ]

    mock_result.__iter__ = lambda self: iter(mock_rows)
    mock_db.execute.return_value = mock_result

    result = get_yoy_growth(mock_db, year=2024)

    assert len(result) == 1
    assert result[0].current_year == 2024
    assert result[0].growth_percent == 14.29
    assert result[0].absolute_growth == 400000.0

    # Verify year filter
    call_args = mock_db.execute.call_args
    assert call_args[1] == {"year": 2024}


# ============================================================================
# UNIT TESTS - get_monthly_summary()
# ============================================================================

@pytest.mark.unit
def test_get_monthly_summary_with_filters():
    """Test get_monthly_summary with year and account_type filters."""
    mock_db = MagicMock()
    mock_result = MagicMock()

    mock_rows = [
        MagicMock(
            year=2024,
            quarter=1,
            month=3,
            year_month="2024-03",
            year_quarter="2024-Q1",
            month_name="March",
            account_type="revenue",
            account_count=10,
            total_amount=1800000.0,
            avg_amount=180000.0,
            min_amount=50000.0,
            max_amount=350000.0,
        ),
    ]

    mock_result.__iter__ = lambda self: iter(mock_rows)
    mock_db.execute.return_value = mock_result

    result = get_monthly_summary(mock_db, year=2024, account_type="revenue")

    assert len(result) == 1
    assert result[0].year == 2024
    assert result[0].month_name == "March"
    assert result[0].account_type == "revenue"
    assert result[0].total_amount == 1800000.0

    # Verify both filters were applied
    call_args = mock_db.execute.call_args
    assert call_args[1] == {"year": 2024, "account_type": "revenue"}
