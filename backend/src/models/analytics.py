"""
Pydantic models for analytics data responses.
"""

from typing import Optional
from pydantic import BaseModel


class MonthlySummary(BaseModel):
    """Monthly summary by account type."""
    year: int
    quarter: int
    month: int
    year_month: str
    year_quarter: str
    month_name: str
    account_type: str
    account_count: int
    total_amount: float
    avg_amount: float
    min_amount: float
    max_amount: float


class CategoryPerformance(BaseModel):
    """Performance by account category."""
    account_category: str
    account_type: str
    year: int
    quarter: int
    year_quarter: str
    account_count: int
    transaction_count: int
    total_amount: float
    avg_amount: float
    min_amount: float
    max_amount: float


class ProfitLoss(BaseModel):
    """Profit & Loss by period."""
    year: int
    quarter: int
    year_quarter: str
    revenue: float
    cogs: float
    expenses: float
    gross_profit: float
    net_profit: float
    profit_margin_percent: Optional[float]


class YoYGrowth(BaseModel):
    """Year-over-year growth metrics."""
    account_category: str
    account_type: str
    current_year: int
    current_amount: float
    previous_amount: float
    absolute_growth: float
    growth_percent: Optional[float]


class TopAccount(BaseModel):
    """Top accounts by amount."""
    account_name: str
    account_type: str
    account_category: str
    year: int
    quarter: Optional[int] = None
    year_quarter: Optional[str] = None
    transaction_count: int
    total_amount: float
    avg_amount: float
    rank_in_type_year: Optional[int] = None
    rank_in_quarter: Optional[int] = None


class TrendAnalysis(BaseModel):
    """Month-over-month trend analysis."""
    account_type: str
    year: int
    month: int
    year_month: str
    month_total: float
    prev_month_total: Optional[float]
    mom_change: Optional[float]
    mom_change_percent: Optional[float]
