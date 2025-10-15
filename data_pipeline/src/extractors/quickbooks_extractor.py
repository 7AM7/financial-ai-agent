"""
QuickBooks data extractor for Profit & Loss reports.
Handles column-based monthly financial data.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional

from src.config.logging_config import get_logger
from src.extractors.base import BaseExtractor

logger = get_logger(__name__)


class QuickBooksExtractor(BaseExtractor):
    """
    Extracts financial data from QuickBooks Profit & Loss format.

    Data structure:
    - Header with metadata (report type, basis, currency, date range)
    - Columns with monthly periods
    - Rows with hierarchical account structure
    """

    def __init__(self, source_path: str):
        super().__init__(source_path)
        self.data: Optional[Dict[str, Any]] = None

    def validate(self) -> bool:
        """Validate QuickBooks data format."""
        try:
            path = Path(self.source_path)
            if not path.exists():
                raise FileNotFoundError(f"Data file not found: {self.source_path}")

            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Validate structure
            if "data" not in data:
                raise ValueError("Missing 'data' key in QuickBooks file")

            if "Header" not in data["data"]:
                raise ValueError("Missing 'Header' in QuickBooks data")

            if "Columns" not in data["data"]:
                raise ValueError("Missing 'Columns' in QuickBooks data")

            if "Rows" not in data["data"]:
                raise ValueError("Missing 'Rows' in QuickBooks data")

            self.data = data["data"]
            logger.info(
                "quickbooks_validation_success",
                report_name=self.data["Header"].get("ReportName"),
                currency=self.data["Header"].get("Currency"),
            )
            return True

        except Exception as e:
            logger.error("quickbooks_validation_failed", error=str(e))
            raise

    def _parse_columns(self) -> List[Dict[str, Any]]:
        """Parse column definitions to extract period information."""
        columns = []
        for col in self.data["Columns"]["Column"]:
            if col["ColType"] == "Money":
                metadata = {item["Name"]: item["Value"] for item in col.get("MetaData", [])}
                columns.append(
                    {
                        "title": col["ColTitle"],
                        "start_date": metadata.get("StartDate"),
                        "end_date": metadata.get("EndDate"),
                        "col_key": metadata.get("ColKey"),
                    }
                )
        return columns

    def _process_row(
        self,
        row: Dict[str, Any],
        columns: List[Dict[str, Any]],
        parent_account: Optional[str] = None,
        account_type: Optional[str] = None,
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Recursively process row and its children.

        Args:
            row: Row data dictionary
            columns: List of column definitions
            parent_account: Parent account name for hierarchy
            account_type: Type of account (revenue, expense, cogs, etc.)
        """
        row_type = row.get("type")

        # Determine account type from section headers
        if row_type == "Section":
            group = row.get("group", "")
            if "Income" in group or "Revenue" in group:
                account_type = "revenue"
            elif "Cost of Goods Sold" in group or "COGS" in group:
                account_type = "cogs"
            elif "Expenses" in group or "Operating Expenses" in group:
                account_type = "expense"

        # Process data rows
        if row_type == "Data":
            account_name = None
            col_data = row.get("ColData", [])

            # First column is account name
            if col_data and len(col_data) > 0:
                account_name = col_data[0].get("value", "").strip()

            if account_name:
                # Extract amounts for each period
                for idx, col_def in enumerate(columns):
                    # Column data starts at index 1 (index 0 is account name)
                    if idx + 1 < len(col_data):
                        amount_str = col_data[idx + 1].get("value", "0")

                        # Clean and parse amount
                        try:
                            amount = float(amount_str.replace(",", "").replace("$", ""))
                        except (ValueError, AttributeError):
                            amount = 0.0

                        # Only yield non-zero amounts
                        if amount != 0.0:
                            yield {
                                "account_name": account_name,
                                "account_type": account_type or "other",
                                "parent_account": parent_account,
                                "period_start": col_def["start_date"],
                                "period_end": col_def["end_date"],
                                "amount": amount,
                                "currency": self.data["Header"].get("Currency", "USD"),
                                "source_system": "quickbooks",
                            }

        # Recursively process child rows
        if "Rows" in row:
            rows = row["Rows"]
            if isinstance(rows, dict) and "Row" in rows:
                child_rows = rows["Row"]
                if not isinstance(child_rows, list):
                    child_rows = [child_rows]

                for child_row in child_rows:
                    # Pass current account as parent for children
                    child_parent = None
                    if row_type == "Data" and col_data and len(col_data) > 0:
                        child_parent = col_data[0].get("value", "").strip()

                    yield from self._process_row(
                        child_row,
                        columns,
                        parent_account=child_parent or parent_account,
                        account_type=account_type,
                    )

    def extract(self) -> Generator[Dict[str, Any], None, None]:
        """
        Extract financial transactions from QuickBooks data.

        Yields:
            Dictionary containing transaction data
        """
        if self.data is None:
            self.validate()

        logger.info("quickbooks_extraction_started", source=self.source_path)

        # Parse column definitions
        columns = self._parse_columns()
        logger.info("quickbooks_columns_parsed", num_columns=len(columns))

        # Process all rows
        rows = self.data.get("Rows", {}).get("Row", [])
        if not isinstance(rows, list):
            rows = [rows]

        record_count = 0
        for row in rows:
            for record in self._process_row(row, columns):
                record_count += 1
                yield record

        logger.info("quickbooks_extraction_completed", records_extracted=record_count)
