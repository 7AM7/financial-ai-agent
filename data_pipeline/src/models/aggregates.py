"""
Aggregate views and materialized views for fast AI queries.
Pre-calculated metrics for common analytical questions.
"""
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.config.logging_config import get_logger

logger = get_logger(__name__)


def create_aggregate_views(db: Session) -> None:
    """
    Create aggregate views for fast AI queries.
    These views pre-calculate common metrics.
    """
    logger.info("creating_aggregate_views")

    # View 1: Monthly Summary by Account Type
    # Answers: "What was revenue/expense in January 2024?"
    monthly_summary_sql = text("""
    CREATE OR REPLACE VIEW v_monthly_summary AS
    SELECT
        d.year,
        d.quarter,
        d.month,
        d.year_month,
        d.year_quarter,
        d.month_name,
        a.account_type,
        COUNT(DISTINCT f.account_key) as account_count,
        SUM(f.amount) as total_amount,
        AVG(f.amount) as avg_amount,
        MIN(f.amount) as min_amount,
        MAX(f.amount) as max_amount
    FROM fact_financials f
    JOIN dim_account a ON f.account_key = a.account_key
    JOIN dim_date d ON f.period_start_key = d.date_key
    GROUP BY d.year, d.quarter, d.month, d.year_month, d.year_quarter, d.month_name, a.account_type;
    """)

    # View 2: Category Performance
    # Answers: "Which expense category is highest?"
    category_performance_sql = text("""
    CREATE OR REPLACE VIEW v_category_performance AS
    SELECT
        a.account_category,
        a.account_type,
        f.year,
        f.quarter,
        f.year_quarter,
        COUNT(DISTINCT f.account_key) as account_count,
        COUNT(*) as transaction_count,
        SUM(f.amount) as total_amount,
        AVG(f.amount) as avg_amount,
        MIN(f.amount) as min_amount,
        MAX(f.amount) as max_amount
    FROM fact_financials f
    JOIN dim_account a ON f.account_key = a.account_key
    WHERE a.account_category IS NOT NULL
    GROUP BY a.account_category, a.account_type, f.year, f.quarter, f.year_quarter;
    """)

    # View 3: Profit & Loss by Period
    # Answers: "What was profit in Q1?"
    profit_loss_sql = text("""
    CREATE OR REPLACE VIEW v_profit_loss AS
    SELECT
        f.year,
        f.quarter,
        f.year_quarter,
        SUM(CASE WHEN a.account_type = 'revenue' THEN f.amount ELSE 0 END) as revenue,
        SUM(CASE WHEN a.account_type = 'cogs' THEN f.amount ELSE 0 END) as cogs,
        SUM(CASE WHEN a.account_type = 'expense' THEN f.amount ELSE 0 END) as expenses,
        SUM(CASE WHEN a.account_type = 'revenue' THEN f.amount ELSE 0 END) -
        SUM(CASE WHEN a.account_type = 'cogs' THEN f.amount ELSE 0 END) as gross_profit,
        SUM(CASE WHEN a.account_type = 'revenue' THEN f.amount ELSE 0 END) -
        SUM(CASE WHEN a.account_type IN ('cogs', 'expense') THEN f.amount ELSE 0 END) as net_profit,
        ROUND(
            (SUM(CASE WHEN a.account_type = 'revenue' THEN f.amount ELSE 0 END) -
             SUM(CASE WHEN a.account_type IN ('cogs', 'expense') THEN f.amount ELSE 0 END)) /
            NULLIF(SUM(CASE WHEN a.account_type = 'revenue' THEN f.amount ELSE 0 END), 0) * 100,
            2
        ) as profit_margin_percent
    FROM fact_financials f
    JOIN dim_account a ON f.account_key = a.account_key
    GROUP BY f.year, f.quarter, f.year_quarter
    ORDER BY f.year, f.quarter;
    """)

    # View 4: YoY Growth by Category
    # Answers: "Which category grew most year-over-year?"
    yoy_growth_sql = text("""
    CREATE OR REPLACE VIEW v_yoy_growth AS
    WITH yearly_totals AS (
        SELECT
            a.account_category,
            a.account_type,
            f.year,
            SUM(f.amount) as year_total
        FROM fact_financials f
        JOIN dim_account a ON f.account_key = a.account_key
        WHERE a.account_category IS NOT NULL
        GROUP BY a.account_category, a.account_type, f.year
    )
    SELECT
        curr.account_category,
        curr.account_type,
        curr.year as current_year,
        curr.year_total as current_amount,
        prev.year_total as previous_amount,
        curr.year_total - COALESCE(prev.year_total, 0) as absolute_growth,
        ROUND(
            (curr.year_total - COALESCE(prev.year_total, 0)) /
            NULLIF(prev.year_total, 0) * 100,
            2
        ) as growth_percent
    FROM yearly_totals curr
    LEFT JOIN yearly_totals prev
        ON curr.account_category = prev.account_category
        AND curr.account_type = prev.account_type
        AND curr.year = prev.year + 1
    WHERE prev.year_total IS NOT NULL OR curr.year > (SELECT MIN(year) FROM yearly_totals)
    ORDER BY curr.year DESC, absolute_growth DESC;
    """)

    # View 5a: Top Accounts by Year
    # Answers: "What are the top 10 expenses in 2024?"
    top_accounts_yearly_sql = text("""
    CREATE OR REPLACE VIEW v_top_accounts_yearly AS
    SELECT
        a.account_name,
        a.account_type,
        a.account_category,
        f.year,
        COUNT(*) as transaction_count,
        SUM(f.amount) as total_amount,
        AVG(f.amount) as avg_amount,
        ROW_NUMBER() OVER (
            PARTITION BY a.account_type, f.year
            ORDER BY SUM(f.amount) DESC
        ) as rank_in_type_year
    FROM fact_financials f
    JOIN dim_account a ON f.account_key = a.account_key
    GROUP BY a.account_name, a.account_type, a.account_category, f.year;
    """)

    # View 5b: Top Accounts by Quarter
    # Answers: "What are the top accounts in Q1 2024?"
    top_accounts_quarterly_sql = text("""
    CREATE OR REPLACE VIEW v_top_accounts_quarterly AS
    SELECT
        a.account_name,
        a.account_type,
        a.account_category,
        f.year,
        f.quarter,
        f.year_quarter,
        COUNT(*) as transaction_count,
        SUM(f.amount) as total_amount,
        AVG(f.amount) as avg_amount,
        ROW_NUMBER() OVER (
            PARTITION BY a.account_type, f.year_quarter
            ORDER BY SUM(f.amount) DESC
        ) as rank_in_quarter
    FROM fact_financials f
    JOIN dim_account a ON f.account_key = a.account_key
    GROUP BY a.account_name, a.account_type, a.account_category, f.year, f.quarter, f.year_quarter;
    """)

    # View 6: Trend Analysis (Month-over-Month)
    # Answers: "Show me revenue trends"
    trend_analysis_sql = text("""
    CREATE OR REPLACE VIEW v_trend_analysis AS
    WITH monthly_data AS (
        SELECT
            a.account_type,
            f.year,
            f.month,
            CONCAT(f.year, '-', LPAD(f.month::text, 2, '0')) as year_month,
            SUM(f.amount) as month_total
        FROM fact_financials f
        JOIN dim_account a ON f.account_key = a.account_key
        GROUP BY a.account_type, f.year, f.month
    )
    SELECT
        account_type,
        year,
        month,
        year_month,
        month_total,
        LAG(month_total, 1) OVER (
            PARTITION BY account_type
            ORDER BY year, month
        ) as prev_month_total,
        month_total - LAG(month_total, 1) OVER (
            PARTITION BY account_type
            ORDER BY year, month
        ) as mom_change,
        ROUND(
            (month_total - LAG(month_total, 1) OVER (
                PARTITION BY account_type
                ORDER BY year, month
            )) / NULLIF(LAG(month_total, 1) OVER (
                PARTITION BY account_type
                ORDER BY year, month
            ), 0) * 100,
            2
        ) as mom_change_percent
    FROM monthly_data
    ORDER BY account_type, year, month;
    """)

    # View 7: AI-Optimized Denormalized View
    # Purpose: Single wide table for AI SQL generation (no JOINs needed)
    ai_financial_data_sql = text("""
    CREATE OR REPLACE VIEW v_ai_financial_data AS
    SELECT
        -- Identifiers
        f.fact_key,

        -- Account information
        a.account_name,
        a.account_type,
        a.account_category,
        a.parent_account_name,

        -- Transaction data
        f.amount,
        f.currency,

        -- Time dimensions (denormalized from fact table)
        f.year,
        f.quarter,
        f.month,
        f.year_quarter,

        -- Date details (from dim_date)
        d_start.date as period_start,
        d_end.date as period_end,
        d_start.month_name,
        d_start.year_month,

        -- Source information
        s.source_name as source_system,
        f.source_record_id

    FROM fact_financials f
    JOIN dim_account a ON f.account_key = a.account_key
    JOIN dim_date d_start ON f.period_start_key = d_start.date_key
    JOIN dim_date d_end ON f.period_end_key = d_end.date_key
    JOIN dim_source s ON f.source_key = s.source_key
    ORDER BY period_start DESC, account_name;
    """)

    # Execute all view creations
    try:
        # Drop old v_top_accounts view if it exists (cleanup)
        db.execute(text("DROP VIEW IF EXISTS v_top_accounts CASCADE"))

        db.execute(monthly_summary_sql)
        db.execute(category_performance_sql)
        db.execute(profit_loss_sql)
        db.execute(yoy_growth_sql)
        db.execute(top_accounts_yearly_sql)
        db.execute(top_accounts_quarterly_sql)
        db.execute(trend_analysis_sql)
        db.execute(ai_financial_data_sql)
        db.commit()
        logger.info("aggregate_views_created", count=8)
    except Exception as e:
        logger.error("aggregate_views_creation_failed", error=str(e))
        db.rollback()
        raise


def create_indexes_for_performance(db: Session) -> None:
    """
    Create additional indexes to optimize AI query performance.
    """
    logger.info("creating_performance_indexes")

    indexes = [
        # For filtering by account name (searches)
        text("CREATE INDEX IF NOT EXISTS idx_account_name_lower ON dim_account(LOWER(account_name))"),

        # For text search on account names
        text("CREATE INDEX IF NOT EXISTS idx_account_name_trgm ON dim_account USING gin(account_name gin_trgm_ops)"),

        # For quick category filtering
        text("CREATE INDEX IF NOT EXISTS idx_account_category_lower ON dim_account(LOWER(account_category)) WHERE account_category IS NOT NULL"),
    ]

    try:
        # Enable pg_trgm extension for text search
        db.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))

        for index_sql in indexes:
            db.execute(index_sql)

        db.commit()
        logger.info("performance_indexes_created", count=len(indexes))
    except Exception as e:
        logger.warning("some_indexes_failed", error=str(e))
        db.rollback()


# View descriptions for AI agent documentation
VIEW_DESCRIPTIONS = {
    "v_monthly_summary": {
        "description": "Monthly aggregated metrics by account type",
        "use_cases": [
            "What was total revenue in January 2024?",
            "Show me expenses by month",
            "What's the average transaction amount per month?"
        ],
        "key_fields": ["year_month", "account_type", "total_amount", "account_count"]
    },
    "v_category_performance": {
        "description": "Performance metrics grouped by account category",
        "use_cases": [
            "Which expense category had highest spending?",
            "Show me marketing expenses by quarter",
            "What's the average payroll expense?"
        ],
        "key_fields": ["account_category", "year_quarter", "total_amount", "transaction_count"]
    },
    "v_profit_loss": {
        "description": "Profit & Loss statement by period with margins",
        "use_cases": [
            "What was profit in Q1 2024?",
            "Show me profit margins by quarter",
            "Compare revenue vs expenses"
        ],
        "key_fields": ["year_quarter", "revenue", "expenses", "net_profit", "profit_margin_percent"]
    },
    "v_yoy_growth": {
        "description": "Year-over-year growth analysis by category",
        "use_cases": [
            "Which category grew most year-over-year?",
            "Show me YoY growth for expenses",
            "What's the growth rate for revenue?"
        ],
        "key_fields": ["account_category", "current_year", "growth_percent", "absolute_growth"]
    },
    "v_top_accounts_yearly": {
        "description": "Top accounts ranked by amount within type and year (no duplicates)",
        "use_cases": [
            "What are the top 10 expenses in 2024?",
            "Show me highest revenue accounts this year",
            "Which accounts had the most spending in 2025?"
        ],
        "key_fields": ["account_name", "year", "total_amount", "rank_in_type_year"]
    },
    "v_top_accounts_quarterly": {
        "description": "Top accounts ranked by amount within type and quarter",
        "use_cases": [
            "What are the top 5 revenue accounts in Q1 2024?",
            "Show me highest expenses in Q3",
            "Which accounts were top performers this quarter?"
        ],
        "key_fields": ["account_name", "year_quarter", "total_amount", "rank_in_quarter"]
    },
    "v_trend_analysis": {
        "description": "Month-over-month trend analysis with change percentages",
        "use_cases": [
            "Show me revenue trends for 2024",
            "What's the month-over-month growth?",
            "How did expenses change month to month?"
        ],
        "key_fields": ["year_month", "month_total", "mom_change", "mom_change_percent"]
    }
}
