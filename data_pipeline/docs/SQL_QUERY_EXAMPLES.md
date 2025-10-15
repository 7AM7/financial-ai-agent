# SQL Query Examples for AI Agent

This document provides SQL query templates that an AI agent can use to answer natural language questions about financial data.

## Database Schema Overview

### Star Schema Design

**Fact Table:** `fact_financials`
- Contains all financial transactions with metrics (amount)
- Denormalized time fields (year, quarter, month, year_quarter) for fast filtering
- Foreign keys to dimension tables

**Dimension Tables:**
- `dim_account` - Account information with categories
- `dim_date` - Date dimension with year/quarter/month
- `dim_source` - Data source information (QuickBooks, Rootfi)

---

## Common Query Patterns

### 1. "What was the total profit in Q1?"

**Approach:** Profit = Revenue - (Expenses + COGS)

```sql
-- Q1 2024 Profit
WITH revenue AS (
    SELECT SUM(f.amount) as total_revenue
    FROM fact_financials f
    JOIN dim_account a ON f.account_key = a.account_key
    WHERE f.year = 2024
      AND f.quarter = 1
      AND a.account_type = 'revenue'
),
costs AS (
    SELECT SUM(f.amount) as total_costs
    FROM fact_financials f
    JOIN dim_account a ON f.account_key = a.account_key
    WHERE f.year = 2024
      AND f.quarter = 1
      AND a.account_type IN ('expense', 'cogs')
)
SELECT
    r.total_revenue - c.total_costs as net_profit,
    r.total_revenue,
    c.total_costs
FROM revenue r, costs c;
```

**Simplified version (using denormalized fields):**

```sql
SELECT
    SUM(CASE WHEN a.account_type = 'revenue' THEN f.amount ELSE 0 END) as revenue,
    SUM(CASE WHEN a.account_type IN ('expense', 'cogs') THEN f.amount ELSE 0 END) as costs,
    SUM(CASE WHEN a.account_type = 'revenue' THEN f.amount ELSE -f.amount END) as profit
FROM fact_financials f
JOIN dim_account a ON f.account_key = a.account_key
WHERE f.year_quarter = '2024-Q1';
```

---

### 2. "Show me revenue trends for 2024"

**Month-over-month revenue:**

```sql
SELECT
    d.year_month,
    d.month_name,
    SUM(f.amount) as revenue
FROM fact_financials f
JOIN dim_account a ON f.account_key = a.account_key
JOIN dim_date d ON f.period_start_key = d.date_key
WHERE f.year = 2024
  AND a.account_type = 'revenue'
GROUP BY d.year_month, d.month_name, d.month
ORDER BY d.year_month;
```

**Quarter-over-quarter revenue:**

```sql
SELECT
    f.year_quarter,
    SUM(f.amount) as revenue,
    LAG(SUM(f.amount)) OVER (ORDER BY f.year_quarter) as previous_quarter_revenue,
    ROUND(
        ((SUM(f.amount) - LAG(SUM(f.amount)) OVER (ORDER BY f.year_quarter)) /
         LAG(SUM(f.amount)) OVER (ORDER BY f.year_quarter)) * 100,
        2
    ) as percent_change
FROM fact_financials f
JOIN dim_account a ON f.account_key = a.account_key
WHERE f.year = 2024
  AND a.account_type = 'revenue'
GROUP BY f.year_quarter
ORDER BY f.year_quarter;
```

---

### 3. "Which expense category had the highest increase this year?"

**Year-over-year category comparison:**

```sql
WITH current_year AS (
    SELECT
        a.account_category,
        SUM(f.amount) as current_amount
    FROM fact_financials f
    JOIN dim_account a ON f.account_key = a.account_key
    WHERE f.year = 2024
      AND a.account_type = 'expense'
      AND a.account_category IS NOT NULL
    GROUP BY a.account_category
),
previous_year AS (
    SELECT
        a.account_category,
        SUM(f.amount) as previous_amount
    FROM fact_financials f
    JOIN dim_account a ON f.account_key = a.account_key
    WHERE f.year = 2023
      AND a.account_type = 'expense'
      AND a.account_category IS NOT NULL
    GROUP BY a.account_category
)
SELECT
    cy.account_category,
    cy.current_amount,
    COALESCE(py.previous_amount, 0) as previous_amount,
    cy.current_amount - COALESCE(py.previous_amount, 0) as absolute_increase,
    ROUND(
        ((cy.current_amount - COALESCE(py.previous_amount, 0)) /
         NULLIF(py.previous_amount, 0)) * 100,
        2
    ) as percent_increase
FROM current_year cy
LEFT JOIN previous_year py ON cy.account_category = py.account_category
ORDER BY absolute_increase DESC
LIMIT 10;
```

---

### 4. "Compare Q1 and Q2 performance"

**Side-by-side quarter comparison:**

```sql
SELECT
    a.account_type,
    SUM(CASE WHEN f.year_quarter = '2024-Q1' THEN f.amount ELSE 0 END) as q1_amount,
    SUM(CASE WHEN f.year_quarter = '2024-Q2' THEN f.amount ELSE 0 END) as q2_amount,
    SUM(CASE WHEN f.year_quarter = '2024-Q2' THEN f.amount ELSE 0 END) -
    SUM(CASE WHEN f.year_quarter = '2024-Q1' THEN f.amount ELSE 0 END) as change,
    ROUND(
        ((SUM(CASE WHEN f.year_quarter = '2024-Q2' THEN f.amount ELSE 0 END) -
          SUM(CASE WHEN f.year_quarter = '2024-Q1' THEN f.amount ELSE 0 END)) /
         NULLIF(SUM(CASE WHEN f.year_quarter = '2024-Q1' THEN f.amount ELSE 0 END), 0)) * 100,
        2
    ) as percent_change
FROM fact_financials f
JOIN dim_account a ON f.account_key = a.account_key
WHERE f.year_quarter IN ('2024-Q1', '2024-Q2')
GROUP BY a.account_type;
```

---

## Advanced Queries

### 5. Top 10 Expense Accounts by Amount

```sql
SELECT
    a.account_name,
    a.account_category,
    SUM(f.amount) as total_expenses,
    COUNT(*) as transaction_count
FROM fact_financials f
JOIN dim_account a ON f.account_key = a.account_key
WHERE a.account_type = 'expense'
  AND f.year = 2024
GROUP BY a.account_name, a.account_category
ORDER BY total_expenses DESC
LIMIT 10;
```

### 6. Monthly Profit Margins

```sql
WITH monthly_metrics AS (
    SELECT
        f.year_month,
        SUM(CASE WHEN a.account_type = 'revenue' THEN f.amount ELSE 0 END) as revenue,
        SUM(CASE WHEN a.account_type IN ('expense', 'cogs') THEN f.amount ELSE 0 END) as costs
    FROM fact_financials f
    JOIN dim_account a ON f.account_key = a.account_key
    WHERE f.year = 2024
    GROUP BY f.year_month
)
SELECT
    year_month,
    revenue,
    costs,
    revenue - costs as profit,
    ROUND(((revenue - costs) / NULLIF(revenue, 0)) * 100, 2) as profit_margin_percent
FROM monthly_metrics
ORDER BY year_month;
```

### 7. Account Growth Analysis

```sql
SELECT
    a.account_name,
    a.account_type,
    f.year,
    SUM(f.amount) as yearly_total,
    LAG(SUM(f.amount)) OVER (PARTITION BY a.account_name ORDER BY f.year) as previous_year_total,
    SUM(f.amount) - LAG(SUM(f.amount)) OVER (PARTITION BY a.account_name ORDER BY f.year) as growth
FROM fact_financials f
JOIN dim_account a ON f.account_key = a.account_key
WHERE a.account_type = 'revenue'
GROUP BY a.account_name, a.account_type, f.year
ORDER BY a.account_name, f.year;
```

### 8. Category Breakdown by Quarter

```sql
SELECT
    f.year_quarter,
    a.account_category,
    COUNT(DISTINCT a.account_key) as account_count,
    SUM(f.amount) as total_amount,
    AVG(f.amount) as avg_transaction
FROM fact_financials f
JOIN dim_account a ON f.account_key = a.account_key
WHERE f.year = 2024
  AND a.account_category IS NOT NULL
GROUP BY f.year_quarter, a.account_category
ORDER BY f.year_quarter, total_amount DESC;
```

---

## AI Agent Query Patterns

### Pattern Matching for Natural Language

| User Query | SQL Pattern | Key Fields |
|-----------|-------------|-----------|
| "total profit in [period]" | SUM with account_type filter | year_quarter, account_type |
| "revenue trends" | GROUP BY time period | year_month, account_type='revenue' |
| "which category increased most" | YoY comparison with ORDER BY | account_category, year |
| "compare [period1] vs [period2]" | CASE WHEN for pivoting | year_quarter |
| "top expenses" | ORDER BY DESC LIMIT | account_type='expense' |
| "profit margin" | (revenue - costs) / revenue | account_type calculation |

### Query Building Tips for AI Agent

1. **Always join dim_account** to filter by account_type
2. **Use denormalized time fields** (year, quarter, year_quarter) for fast filtering
3. **Use LAG/LEAD** for period-over-period comparisons
4. **Use CASE WHEN** for pivoting quarters/periods
5. **Filter nulls** in account_category when grouping
6. **Use NULLIF** to avoid division by zero

---

## Performance Optimization

### Indexes Available

```sql
-- On fact_financials
idx_year_quarter_account (year_quarter, account_key)
idx_time_series (year, quarter, month, account_key, amount)
idx_period_account (period_start_key, period_end_key, account_key)

-- On dim_account
idx_account_type_category (account_type, account_category)
idx_account_name_search (account_name)

-- On dim_date
idx_year_quarter (year, quarter)
idx_year_month (year, month)
```

### Query Optimization Tips

1. **Use denormalized fields** (year, quarter, year_quarter) instead of joining dim_date when possible
2. **Filter early** - add WHERE clauses before joins
3. **Limit result sets** - use LIMIT for large queries
4. **Use covering indexes** - idx_time_series covers most time-based queries
5. **Avoid SELECT *** - specify needed columns only

---

## Schema Reference

### fact_financials
```sql
fact_key            BIGINT PRIMARY KEY
account_key         BIGINT (FK to dim_account)
period_start_key    INTEGER (FK to dim_date)
period_end_key      INTEGER (FK to dim_date)
source_key          INTEGER (FK to dim_source)
amount              NUMERIC(20,2)
currency            VARCHAR(10)
year                INTEGER
quarter             INTEGER
month               INTEGER
year_quarter        VARCHAR(10)  -- "2024-Q1"
```

### dim_account
```sql
account_key         BIGINT PRIMARY KEY
account_id          VARCHAR(255) UNIQUE
account_name        VARCHAR(500)
account_type        VARCHAR(100)  -- 'revenue', 'expense', 'cogs'
account_category    VARCHAR(200)  -- Grouping category
parent_account_name VARCHAR(500)
is_parent           BOOLEAN
source_system       VARCHAR(50)
```

### dim_date
```sql
date_key            INTEGER PRIMARY KEY  -- YYYYMMDD format
date                DATE
year                INTEGER
quarter             INTEGER (1-4)
month               INTEGER (1-12)
month_name          VARCHAR(20)
year_quarter        VARCHAR(10)  -- "2024-Q1"
year_month          VARCHAR(10)  -- "2024-01"
```

---

## Example AI Agent Response Format

**User:** "What was the total profit in Q1?"

**AI Agent Process:**
1. Parse: "profit" → revenue - expenses, "Q1" → quarter 1, "current year" implied
2. Generate SQL using pattern from Example #1
3. Execute query
4. Format response: "The total profit in Q1 2024 was $XXX,XXX, with revenue of $XXX,XXX and costs of $XXX,XXX."

This star schema design makes it easy for AI agents to:
- Quickly identify relevant tables
- Build efficient queries
- Aggregate by time periods
- Group by categories
- Compare periods
