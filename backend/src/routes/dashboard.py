"""
Dashboard routes for analytics endpoints.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.db import get_db
from src.services.analytics_service import (
    get_monthly_summary,
    get_category_performance,
    get_profit_loss,
    get_yoy_growth,
    get_top_accounts,
    get_trend_analysis,
)


router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/monthly-summary")
def api_monthly_summary(
    year: Optional[int] = None,
    account_type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Get monthly summary data.

    Query params:
    - year: Filter by year (e.g., 2024)
    - account_type: Filter by type (revenue, expense, cogs)
    """
    try:
        data = get_monthly_summary(db, year=year, account_type=account_type)
        return {"data": [d.model_dump() for d in data]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/category-performance")
def api_category_performance(
    account_type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Get category performance data.

    Query params:
    - account_type: Filter by type (revenue, expense, cogs)
    """
    try:
        data = get_category_performance(db, account_type=account_type)
        return {"data": [d.model_dump() for d in data]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profit-loss")
def api_profit_loss(
    year: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """
    Get profit & loss data.

    Query params:
    - year: Filter by year (e.g., 2024)
    """
    try:
        data = get_profit_loss(db, year=year)
        return {"data": [d.model_dump() for d in data]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/yoy-growth")
def api_yoy_growth(
    year: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """
    Get year-over-year growth metrics.

    Query params:
    - year: Filter by year (e.g., 2024)
    """
    try:
        data = get_yoy_growth(db, year=year)
        return {"data": [d.model_dump() for d in data]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-accounts")
def api_top_accounts(
    account_type: Optional[str] = None,
    year: Optional[int] = None,
    period: str = "yearly",
    limit: int = 10,
    db: Session = Depends(get_db),
):
    """
    Get top accounts by total amount.

    Query params:
    - account_type: Filter by type (revenue, expense, cogs)
    - year: Filter by year (e.g., 2025)
    - period: 'yearly' or 'quarterly' (default: 'yearly')
    - limit: Number of accounts (default: 10)
    """
    try:
        data = get_top_accounts(db, account_type=account_type, year=year, period=period, limit=limit)
        return {"data": [d.model_dump() for d in data]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trend-analysis")
def api_trend_analysis(
    year: Optional[int] = None,
    account_type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Get month-over-month trend analysis.

    Query params:
    - year: Filter by year (e.g., 2024)
    - account_type: Filter by type (revenue, expense, cogs)
    """
    try:
        data = get_trend_analysis(db, year=year, account_type=account_type)
        return {"data": [d.model_dump() for d in data]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/overview")
def api_dashboard_overview(db: Session = Depends(get_db)):
    """
    Get dashboard overview with key metrics.

    Returns summary data for quick visualization.
    """
    try:
        latest_year_result = db.execute(
            text("SELECT MAX(year) as max_year FROM fact_financials")
        )
        latest_year_row = latest_year_result.fetchone()
        latest_year = latest_year_row.max_year if latest_year_row else 2024

        return {
            "profit_loss": [d.model_dump() for d in get_profit_loss(db, year=latest_year)],
            "top_expenses": [d.model_dump() for d in get_top_accounts(db, account_type="expense", limit=5)],
            "top_revenue": [d.model_dump() for d in get_top_accounts(db, account_type="revenue", limit=5)],
            "trends": [d.model_dump() for d in get_trend_analysis(db, year=latest_year)],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
