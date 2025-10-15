"""
Analytics service for dashboard data endpoints.
Exposes pre-calculated aggregate views for frontend charts.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.models import (
    MonthlySummary,
    CategoryPerformance,
    ProfitLoss,
    YoYGrowth,
    TopAccount,
    TrendAnalysis,
)


# ============================================================================
# QUERY FUNCTIONS
# ============================================================================

def get_monthly_summary(
    db: Session,
    year: Optional[int] = None,
    account_type: Optional[str] = None
) -> List[MonthlySummary]:
    """
    Get monthly summary data for charts.

    Args:
        db: Database session
        year: Optional year filter
        account_type: Optional account type filter (revenue, expense, cogs)

    Returns:
        List of monthly summaries
    """
    query = "SELECT * FROM v_monthly_summary WHERE 1=1"
    params = {}

    if year:
        query += " AND year = :year"
        params["year"] = year

    if account_type:
        query += " AND account_type = :account_type"
        params["account_type"] = account_type

    query += " ORDER BY year DESC, month DESC"

    result = db.execute(text(query), params)
    return [
        MonthlySummary(
            year=row.year,
            quarter=row.quarter,
            month=row.month,
            year_month=row.year_month,
            year_quarter=row.year_quarter,
            month_name=row.month_name,
            account_type=row.account_type,
            account_count=row.account_count,
            total_amount=float(row.total_amount),
            avg_amount=float(row.avg_amount),
            min_amount=float(row.min_amount),
            max_amount=float(row.max_amount),
        )
        for row in result
    ]


def get_category_performance(
    db: Session,
    account_type: Optional[str] = None
) -> List[CategoryPerformance]:
    """
    Get category performance data.

    Args:
        db: Database session
        account_type: Optional account type filter

    Returns:
        List of category performance metrics
    """
    query = "SELECT * FROM v_category_performance WHERE 1=1"
    params = {}

    if account_type:
        query += " AND account_type = :account_type"
        params["account_type"] = account_type

    query += " ORDER BY total_amount DESC"

    result = db.execute(text(query), params)
    return [
        CategoryPerformance(
            account_category=row.account_category,
            account_type=row.account_type,
            year=row.year,
            quarter=row.quarter,
            year_quarter=row.year_quarter,
            account_count=row.account_count,
            transaction_count=row.transaction_count,
            total_amount=float(row.total_amount),
            avg_amount=float(row.avg_amount),
            min_amount=float(row.min_amount),
            max_amount=float(row.max_amount),
        )
        for row in result
    ]


def get_profit_loss(
    db: Session,
    year: Optional[int] = None
) -> List[ProfitLoss]:
    """
    Get profit & loss data.

    Args:
        db: Database session
        year: Optional year filter

    Returns:
        List of P&L by period
    """
    query = "SELECT * FROM v_profit_loss WHERE 1=1"
    params = {}

    if year:
        query += " AND year = :year"
        params["year"] = year

    query += " ORDER BY year DESC, quarter DESC"

    result = db.execute(text(query), params)
    return [
        ProfitLoss(
            year=row.year,
            quarter=row.quarter,
            year_quarter=row.year_quarter,
            revenue=float(row.revenue),
            cogs=float(row.cogs),
            expenses=float(row.expenses),
            gross_profit=float(row.gross_profit),
            net_profit=float(row.net_profit),
            profit_margin_percent=float(row.profit_margin_percent) if row.profit_margin_percent else None,
        )
        for row in result
    ]


def get_yoy_growth(
    db: Session,
    year: Optional[int] = None
) -> List[YoYGrowth]:
    """
    Get year-over-year growth metrics.

    Args:
        db: Database session
        year: Optional year filter

    Returns:
        List of YoY growth metrics
    """
    query = "SELECT * FROM v_yoy_growth WHERE 1=1"
    params = {}

    if year:
        query += " AND current_year = :year"
        params["year"] = year

    query += " ORDER BY current_year DESC, growth_percent DESC NULLS LAST"

    result = db.execute(text(query), params)
    return [
        YoYGrowth(
            account_category=row.account_category,
            account_type=row.account_type,
            current_year=row.current_year,
            current_amount=float(row.current_amount),
            previous_amount=float(row.previous_amount),
            absolute_growth=float(row.absolute_growth),
            growth_percent=float(row.growth_percent) if row.growth_percent else None,
        )
        for row in result
    ]


def get_top_accounts(
    db: Session,
    account_type: Optional[str] = None,
    year: Optional[int] = None,
    period: str = "yearly",
    limit: int = 10
) -> List[TopAccount]:
    """
    Get top accounts by total amount.

    Args:
        db: Database session
        account_type: Optional account type filter
        year: Optional year filter
        period: 'yearly' or 'quarterly' (default: 'yearly')
        limit: Number of accounts to return

    Returns:
        List of top accounts
    """
    # Choose view based on period
    view_name = "v_top_accounts_yearly" if period == "yearly" else "v_top_accounts_quarterly"
    rank_field = "rank_in_type_year" if period == "yearly" else "rank_in_quarter"

    query = f"SELECT * FROM {view_name} WHERE 1=1"
    params = {"limit": limit}

    if account_type:
        query += " AND account_type = :account_type"
        params["account_type"] = account_type

    if year:
        query += " AND year = :year"
        params["year"] = year

    query += f" AND {rank_field} <= :limit ORDER BY year DESC, total_amount DESC"

    result = db.execute(text(query), params)

    if period == "yearly":
        return [
            TopAccount(
                account_name=row.account_name,
                account_type=row.account_type,
                account_category=row.account_category,
                year=row.year,
                transaction_count=row.transaction_count,
                total_amount=float(row.total_amount),
                avg_amount=float(row.avg_amount),
                rank_in_type_year=row.rank_in_type_year,
            )
            for row in result
        ]
    else:
        return [
            TopAccount(
                account_name=row.account_name,
                account_type=row.account_type,
                account_category=row.account_category,
                year=row.year,
                quarter=row.quarter,
                year_quarter=row.year_quarter,
                transaction_count=row.transaction_count,
                total_amount=float(row.total_amount),
                avg_amount=float(row.avg_amount),
                rank_in_quarter=row.rank_in_quarter,
            )
            for row in result
        ]


def get_trend_analysis(
    db: Session,
    year: Optional[int] = None,
    account_type: Optional[str] = None
) -> List[TrendAnalysis]:
    """
    Get month-over-month trend analysis.

    Args:
        db: Database session
        year: Optional year filter
        account_type: Optional account type filter

    Returns:
        List of trend data
    """
    query = "SELECT * FROM v_trend_analysis WHERE 1=1"
    params = {}

    if year:
        query += " AND year = :year"
        params["year"] = year

    if account_type:
        query += " AND account_type = :account_type"
        params["account_type"] = account_type

    query += " ORDER BY year DESC, month DESC"

    result = db.execute(text(query), params)
    return [
        TrendAnalysis(
            account_type=row.account_type,
            year=row.year,
            month=row.month,
            year_month=row.year_month,
            month_total=float(row.month_total),
            prev_month_total=float(row.prev_month_total) if row.prev_month_total else None,
            mom_change=float(row.mom_change) if row.mom_change else None,
            mom_change_percent=float(row.mom_change_percent) if row.mom_change_percent else None,
        )
        for row in result
    ]
