"""
Data transformation logic for financial records.
Normalizes and enriches data from different sources.
"""
import hashlib
from datetime import datetime
from typing import Any, Dict, Optional

from src.config.logging_config import get_logger
from src.utils.category_mapper import map_account_category

logger = get_logger(__name__)


class FinancialTransformer:
    """Transforms and normalizes financial data from various sources."""

    def __init__(self):
        self.account_cache: Dict[str, str] = {}

    @staticmethod
    def _generate_account_id(
        account_name: str, account_type: str, source_system: str
    ) -> str:
        """
        Generate unique account ID from name, type, and source.

        Args:
            account_name: Account name
            account_type: Account type
            source_system: Source system name

        Returns:
            Unique account ID
        """
        key = f"{source_system}:{account_type}:{account_name}".lower()
        return hashlib.sha256(key.encode()).hexdigest()[:16]

    @staticmethod
    def _parse_date(date_str: str) -> Optional[datetime]:
        """
        Parse date string from various formats.

        Args:
            date_str: Date string

        Returns:
            Parsed datetime or None if parsing fails
        """
        if not date_str:
            return None

        formats = [
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%S%z",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str.split("T")[0], "%Y-%m-%d")
            except (ValueError, AttributeError):
                continue

        logger.warning("date_parse_failed", date_str=date_str)
        return None

    def transform_transaction(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform raw transaction data into normalized format.

        Args:
            raw_data: Raw transaction data from extractor

        Returns:
            Normalized transaction data
        """
        account_name = raw_data.get("account_name", "").strip()
        account_type = raw_data.get("account_type", "other")
        source_system = raw_data.get("source_system", "unknown")

        # Generate consistent account ID
        account_id = self._generate_account_id(account_name, account_type, source_system)

        # Parse dates
        period_start = self._parse_date(raw_data.get("period_start"))
        period_end = self._parse_date(raw_data.get("period_end"))

        if not period_start or not period_end:
            raise ValueError(f"Invalid period dates: {raw_data}")

        # Normalize amount (expenses should be positive)
        amount = float(raw_data.get("amount", 0.0))

        # Map to standardized category
        parent_account = raw_data.get("parent_account")
        account_category = map_account_category(
            account_name,
            account_type,
            parent_account
        )

        return {
            "account_id": account_id,
            "account_name": account_name,
            "account_type": account_type,
            "account_category": account_category,
            "parent_account": parent_account,
            "source_system": source_system,
            "source_account_id": raw_data.get("source_account_id"),
            "period_start": period_start.date(),
            "period_end": period_end.date(),
            "amount": amount,
            "currency": raw_data.get("currency", "USD"),
            "source_record_id": raw_data.get("source_record_id"),
        }

    def transform_account(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform account data.

        Args:
            raw_data: Raw account data

        Returns:
            Normalized account data
        """
        account_name = raw_data.get("account_name", "").strip()
        account_type = raw_data.get("account_type", "other")
        source_system = raw_data.get("source_system", "unknown")

        account_id = self._generate_account_id(account_name, account_type, source_system)

        # Cache for deduplication
        cache_key = account_id
        if cache_key in self.account_cache:
            return None  # Already processed

        self.account_cache[cache_key] = account_id

        return {
            "account_id": account_id,
            "account_name": account_name,
            "account_type": account_type,
            "parent_account_id": raw_data.get("parent_account"),
            "source_system": source_system,
            "source_account_id": raw_data.get("source_account_id"),
        }
