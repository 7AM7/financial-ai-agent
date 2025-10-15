"""
Star Schema for Financial Data - Optimized for AI/ML Queries.

Design Philosophy:
- Fact table: financial_facts (transaction-level metrics)
- Dimension tables: dim_account, dim_date, dim_source
- Denormalized for fast queries
- Pre-calculated metrics for common aggregations
"""
from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    DateTime
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin


class DimAccount(Base, TimestampMixin):
    """
    Dimension: Account information with hierarchy.
    Enables queries like: "Which expense category had highest increase?"
    """

    __tablename__ = "dim_account"

    account_key: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    account_id: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    account_name: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    account_type: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )  # revenue, expense, cogs
    account_category: Mapped[Optional[str]] = mapped_column(
        String(200), nullable=True, index=True
    )  # Grouping: Payroll, Marketing, Sales, etc.
    parent_account_name: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True
    )
    is_parent: Mapped[bool] = mapped_column(Boolean, default=False)
    source_system: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    source_account_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    facts: Mapped[list["FinancialFact"]] = relationship(back_populates="account")

    __table_args__ = (
        Index("idx_account_type_category", "account_type", "account_category"),
        Index("idx_account_name_search", "account_name"),
    )

    def __repr__(self) -> str:
        return f"<DimAccount(name={self.account_name}, type={self.account_type})>"


class DimDate(Base):
    """
    Dimension: Date information for time-based queries.
    Enables queries like: "Show revenue trends for 2024" or "Q1 profit"
    """

    __tablename__ = "dim_date"

    date_key: Mapped[int] = mapped_column(Integer, primary_key=True)  # YYYYMMDD format
    date: Mapped[date] = mapped_column(Date, nullable=False, unique=True, index=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    quarter: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    month: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    month_name: Mapped[str] = mapped_column(String(20), nullable=False)
    year_quarter: Mapped[str] = mapped_column(
        String(10), nullable=False, index=True
    )  # "2024-Q1"
    year_month: Mapped[str] = mapped_column(
        String(10), nullable=False, index=True
    )  # "2024-01"

    # Relationships
    facts_start: Mapped[list["FinancialFact"]] = relationship(
        back_populates="date_start", foreign_keys="FinancialFact.period_start_key"
    )
    facts_end: Mapped[list["FinancialFact"]] = relationship(
        back_populates="date_end", foreign_keys="FinancialFact.period_end_key"
    )

    __table_args__ = (
        Index("idx_year_quarter", "year", "quarter"),
        Index("idx_year_month", "year", "month"),
    )

    def __repr__(self) -> str:
        return f"<DimDate(date={self.date}, quarter={self.year_quarter})>"


class DimSource(Base, TimestampMixin):
    """
    Dimension: Data source information.
    Simple lookup for source systems.
    """

    __tablename__ = "dim_source"

    source_key: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_name: Mapped[str] = mapped_column(
        String(50), nullable=False, unique=True, index=True
    )
    source_description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    facts: Mapped[list["FinancialFact"]] = relationship(back_populates="source")

    def __repr__(self) -> str:
        return f"<DimSource(name={self.source_name})>"


class FinancialFact(Base, TimestampMixin):
    """
    Fact Table: Core transaction data with metrics.
    Optimized for analytical queries and aggregations.

    Example queries this enables:
    - Total profit by quarter
    - Revenue trends over time
    - Expense category comparisons
    - Period-over-period analysis
    """

    __tablename__ = "fact_financials"

    fact_key: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )

    # Foreign Keys to Dimensions
    account_key: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("dim_account.account_key", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    period_start_key: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("dim_date.date_key", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    period_end_key: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("dim_date.date_key", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_key: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("dim_source.source_key", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Metrics (the "measures" in star schema)
    amount: Mapped[float] = mapped_column(Numeric(20, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)

    # Denormalized fields for fast filtering (avoid joins)
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    quarter: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    month: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    year_quarter: Mapped[str] = mapped_column(String(10), nullable=False, index=True)

    # Metadata
    source_record_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    account: Mapped["DimAccount"] = relationship(back_populates="facts")
    date_start: Mapped["DimDate"] = relationship(
        back_populates="facts_start", foreign_keys=[period_start_key]
    )
    date_end: Mapped["DimDate"] = relationship(
        back_populates="facts_end", foreign_keys=[period_end_key]
    )
    source: Mapped["DimSource"] = relationship(back_populates="facts")

    __table_args__ = (
        # Composite indexes for common query patterns
        Index("idx_year_quarter_account", "year_quarter", "account_key"),
        Index("idx_year_account_type", "year", "account_key"),
        Index("idx_period_account", "period_start_key", "period_end_key", "account_key"),
        # Covering index for time-series queries
        Index("idx_time_series", "year", "quarter", "month", "account_key", "amount"),
    )

    def __repr__(self) -> str:
        return (
            f"<FinancialFact(account_key={self.account_key}, "
            f"year_quarter={self.year_quarter}, amount={self.amount})>"
        )


class PipelineRun(Base, TimestampMixin):
    """Track pipeline execution for monitoring."""

    __tablename__ = "pipeline_runs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    source_system: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    records_processed: Mapped[int] = mapped_column(BigInteger, default=0)
    records_failed: Mapped[int] = mapped_column(BigInteger, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False  # type: ignore
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True  # type: ignore
    )

    __table_args__ = (Index("idx_run_status", "status", "source_system"),)

    def __repr__(self) -> str:
        return f"<PipelineRun(run_id={self.run_id}, status={self.status})>"
