"""
Rootfi data extractor for period-based financial statements.
Handles nested hierarchical line items structure.
"""
import json
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional

from src.config.logging_config import get_logger
from src.extractors.base import BaseExtractor

logger = get_logger(__name__)


class RootfiExtractor(BaseExtractor):
    """
    Extracts financial data from Rootfi format.

    Data structure:
    - Array of period records
    - Each record has revenue, COGS, operating_expenses with nested line_items
    - Hierarchical structure with account IDs
    """

    def __init__(self, source_path: str):
        super().__init__(source_path)
        self.data: Optional[List[Dict[str, Any]]] = None

    def validate(self) -> bool:
        """Validate Rootfi data format."""
        try:
            path = Path(self.source_path)
            if not path.exists():
                raise FileNotFoundError(f"Data file not found: {self.source_path}")

            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Validate structure
            if "data" not in data:
                raise ValueError("Missing 'data' key in Rootfi file")

            if not isinstance(data["data"], list):
                raise ValueError("'data' should be a list of period records")

            if len(data["data"]) == 0:
                raise ValueError("Empty data array in Rootfi file")

            # Validate first record has required fields
            first_record = data["data"][0]
            required_fields = ["period_start", "period_end"]
            for field in required_fields:
                if field not in first_record:
                    raise ValueError(f"Missing required field: {field}")

            self.data = data["data"]
            logger.info(
                "rootfi_validation_success",
                num_periods=len(self.data),
                first_period=first_record.get("period_start"),
                last_period=data["data"][-1].get("period_end"),
            )
            return True

        except Exception as e:
            logger.error("rootfi_validation_failed", error=str(e))
            raise

    def _process_line_items(
        self,
        line_items: List[Dict[str, Any]],
        account_type: str,
        parent_name: Optional[str] = None,
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Recursively process nested line items.

        Only yields leaf nodes (items without children) to avoid double-counting.
        Parent items with children are skipped, as their values are sums of children.

        Args:
            line_items: List of line item dictionaries
            account_type: Type of account (revenue, expense, cogs)
            parent_name: Parent account name for hierarchy
        """
        for item in line_items:
            name = item.get("name", "").strip()
            value = item.get("value", 0)
            account_id = item.get("account_id")

            if name:
                # Check if this item has children (is a parent/rollup item)
                has_children = bool(item.get("line_items"))

                if has_children:
                    # Skip parent item (its value is sum of children)
                    # Only process children recursively
                    logger.debug(
                        "skipping_parent_item",
                        item_name=name,
                        amount=value,
                        reason="has_children"
                    )
                    yield from self._process_line_items(
                        item["line_items"],
                        account_type=account_type,
                        parent_name=name,  # Pass this item as parent for children
                    )
                else:
                    # Leaf node - yield it
                    yield {
                        "account_name": name,
                        "account_type": account_type,
                        "parent_account": parent_name,
                        "amount": float(value) if value is not None else 0.0,
                        "source_account_id": account_id,
                    }

    def _extract_period(self, record: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
        """
        Extract all transactions from a single period record.

        Args:
            record: Period record dictionary
        """
        period_start = record.get("period_start")
        period_end = record.get("period_end")
        currency_id = record.get("currency_id", "USD")

        if not period_start or not period_end:
            logger.warning("period_missing_dates", record_id=record.get("rootfi_id"))
            return

        # Extract revenue
        if "revenue" in record and record["revenue"]:
            for revenue_section in record["revenue"]:
                if "line_items" in revenue_section:
                    for item_data in self._process_line_items(
                        revenue_section["line_items"],
                        account_type="revenue",
                        parent_name=revenue_section.get("name"),
                    ):
                        yield {
                            **item_data,
                            "period_start": period_start,
                            "period_end": period_end,
                            "currency": currency_id or "USD",
                            "source_system": "rootfi",
                            "source_record_id": str(record.get("rootfi_id", "")),
                        }

        # Extract cost of goods sold
        if "cost_of_goods_sold" in record and record["cost_of_goods_sold"]:
            for cogs_section in record["cost_of_goods_sold"]:
                if "line_items" in cogs_section:
                    for item_data in self._process_line_items(
                        cogs_section["line_items"],
                        account_type="cogs",
                        parent_name=cogs_section.get("name"),
                    ):
                        yield {
                            **item_data,
                            "period_start": period_start,
                            "period_end": period_end,
                            "currency": currency_id or "USD",
                            "source_system": "rootfi",
                            "source_record_id": str(record.get("rootfi_id", "")),
                        }

        # Extract operating expenses
        if "operating_expenses" in record and record["operating_expenses"]:
            for expense_section in record["operating_expenses"]:
                if "line_items" in expense_section:
                    for item_data in self._process_line_items(
                        expense_section["line_items"],
                        account_type="expense",
                        parent_name=expense_section.get("name"),
                    ):
                        yield {
                            **item_data,
                            "period_start": period_start,
                            "period_end": period_end,
                            "currency": currency_id or "USD",
                            "source_system": "rootfi",
                            "source_record_id": str(record.get("rootfi_id", "")),
                        }

    def extract(self) -> Generator[Dict[str, Any], None, None]:
        """
        Extract financial transactions from Rootfi data.

        Yields:
            Dictionary containing transaction data
        """
        if self.data is None:
            self.validate()

        logger.info("rootfi_extraction_started", source=self.source_path)

        record_count = 0
        for period_record in self.data:
            for transaction in self._extract_period(period_record):
                # Only yield non-zero amounts
                if transaction["amount"] != 0.0:
                    record_count += 1
                    yield transaction

        logger.info("rootfi_extraction_completed", records_extracted=record_count)
