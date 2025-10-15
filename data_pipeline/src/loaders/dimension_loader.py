"""
Dimension loaders for star schema.
Handles loading and lookups for dimension tables.
"""
from datetime import date, datetime
from typing import Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from src.config.logging_config import get_logger
from src.models.financial import DimAccount, DimDate, DimSource

logger = get_logger(__name__)


class DimensionLoader:
    """Loads and manages dimension tables."""

    def __init__(self, db: Session):
        self.db = db
        self._date_cache: Dict[date, int] = {}
        self._account_cache: Dict[str, int] = {}
        self._source_cache: Dict[str, int] = {}

    def load_date_dimension(self, start_date: date, end_date: date) -> None:
        """
        Pre-populate date dimension for date range.

        Args:
            start_date: Start date
            end_date: End date
        """
        logger.info("date_dimension_loading", start=start_date, end=end_date)

        dates_to_insert = []
        current_date = start_date

        while current_date <= end_date:
            date_key = int(current_date.strftime("%Y%m%d"))
            quarter = (current_date.month - 1) // 3 + 1
            year_quarter = f"{current_date.year}-Q{quarter}"
            year_month = current_date.strftime("%Y-%m")
            month_name = current_date.strftime("%B")

            dates_to_insert.append(
                {
                    "date_key": date_key,
                    "date": current_date,
                    "year": current_date.year,
                    "quarter": quarter,
                    "month": current_date.month,
                    "month_name": month_name,
                    "year_quarter": year_quarter,
                    "year_month": year_month,
                }
            )

            # Move to next day
            from datetime import timedelta

            current_date += timedelta(days=1)

        # Bulk insert with ON CONFLICT DO NOTHING
        if dates_to_insert:
            stmt = pg_insert(DimDate).values(dates_to_insert)
            stmt = stmt.on_conflict_do_nothing(index_elements=["date"])
            self.db.execute(stmt)
            self.db.commit()

        logger.info("date_dimension_loaded", count=len(dates_to_insert))

    def get_date_key(self, date_value: date) -> int:
        """
        Get date key for a date, with caching.

        Args:
            date_value: Date to lookup

        Returns:
            Date key (YYYYMMDD format)
        """
        if date_value in self._date_cache:
            return self._date_cache[date_value]

        date_key = int(date_value.strftime("%Y%m%d"))
        self._date_cache[date_value] = date_key
        return date_key

    def upsert_account(
        self,
        account_id: str,
        account_name: str,
        account_type: str,
        account_category: Optional[str],
        parent_account_name: Optional[str],
        is_parent: bool,
        source_system: str,
        source_account_id: Optional[str],
    ) -> int:
        """
        Upsert account dimension and return account_key.

        Args:
            account_id: Unique account identifier
            account_name: Account name
            account_type: Account type (revenue, expense, cogs)
            account_category: Category grouping
            parent_account_name: Parent account name
            is_parent: Whether this is a parent account
            source_system: Source system name
            source_account_id: Original source account ID

        Returns:
            account_key (surrogate key)
        """
        # Check cache first
        if account_id in self._account_cache:
            return self._account_cache[account_id]

        # Upsert
        stmt = pg_insert(DimAccount).values(
            account_id=account_id,
            account_name=account_name,
            account_type=account_type,
            account_category=account_category,
            parent_account_name=parent_account_name,
            is_parent=is_parent,
            source_system=source_system,
            source_account_id=source_account_id,
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=["account_id"],
            set_={
                "account_name": stmt.excluded.account_name,
                "account_type": stmt.excluded.account_type,
                "account_category": stmt.excluded.account_category,
                "parent_account_name": stmt.excluded.parent_account_name,
                "is_parent": stmt.excluded.is_parent,
                "updated_at": datetime.utcnow(),
            },
        )
        stmt = stmt.returning(DimAccount.account_key)

        result = self.db.execute(stmt)
        account_key = result.scalar_one()
        self.db.commit()

        # Cache it
        self._account_cache[account_id] = account_key
        return account_key

    def get_or_create_source(self, source_name: str, description: str = None) -> int:
        """
        Get or create source dimension.

        Args:
            source_name: Source system name
            description: Optional description

        Returns:
            source_key (surrogate key)
        """
        # Check cache
        if source_name in self._source_cache:
            return self._source_cache[source_name]

        # Try to find existing
        stmt = select(DimSource.source_key).where(DimSource.source_name == source_name)
        result = self.db.execute(stmt).scalar_one_or_none()

        if result:
            self._source_cache[source_name] = result
            return result

        # Create new
        source = DimSource(source_name=source_name, source_description=description)
        self.db.add(source)
        self.db.commit()
        self.db.refresh(source)

        self._source_cache[source_name] = source.source_key
        return source.source_key
