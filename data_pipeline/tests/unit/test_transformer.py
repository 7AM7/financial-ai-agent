"""
Unit tests for financial data transformer.
"""
import pytest
from datetime import date

from data_pipeline.src.transformers.financial_transformer import FinancialTransformer


class TestFinancialTransformer:
    """Test cases for FinancialTransformer."""

    @pytest.fixture
    def transformer(self):
        """Create transformer instance."""
        return FinancialTransformer()

    def test_generate_account_id_consistency(self, transformer):
        """Test that account ID generation is consistent."""
        id1 = transformer._generate_account_id("Revenue", "revenue", "quickbooks")
        id2 = transformer._generate_account_id("Revenue", "revenue", "quickbooks")
        assert id1 == id2

    def test_generate_account_id_uniqueness(self, transformer):
        """Test that different accounts get different IDs."""
        id1 = transformer._generate_account_id("Revenue", "revenue", "quickbooks")
        id2 = transformer._generate_account_id("Expenses", "expense", "quickbooks")
        assert id1 != id2

    def test_parse_date_valid(self, transformer):
        """Test parsing valid date formats."""
        result = transformer._parse_date("2024-01-15")
        assert result is not None
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_parse_date_with_time(self, transformer):
        """Test parsing date with time component."""
        result = transformer._parse_date("2024-01-15T10:30:00")
        assert result is not None
        assert result.year == 2024

    def test_parse_date_invalid(self, transformer):
        """Test parsing invalid date."""
        result = transformer._parse_date("invalid-date")
        assert result is None

    def test_transform_transaction(self, transformer):
        """Test transaction transformation."""
        raw_data = {
            "account_name": "Sales Revenue",
            "account_type": "revenue",
            "source_system": "quickbooks",
            "period_start": "2024-01-01",
            "period_end": "2024-01-31",
            "amount": 10000.50,
            "currency": "USD",
        }

        result = transformer.transform_transaction(raw_data)

        assert result["account_name"] == "Sales Revenue"
        assert result["account_type"] == "revenue"
        assert result["source_system"] == "quickbooks"
        assert result["amount"] == 10000.50
        assert result["currency"] == "USD"
        assert isinstance(result["period_start"], date)
        assert isinstance(result["period_end"], date)
        assert result["account_id"] is not None

    def test_transform_transaction_missing_dates(self, transformer):
        """Test that missing dates raise error."""
        raw_data = {
            "account_name": "Test Account",
            "account_type": "revenue",
            "source_system": "test",
            "amount": 100,
        }

        with pytest.raises(ValueError):
            transformer.transform_transaction(raw_data)

    def test_transform_account(self, transformer):
        """Test account transformation."""
        raw_data = {
            "account_name": "Operating Expenses",
            "account_type": "expense",
            "source_system": "rootfi",
            "source_account_id": "ACC123",
            "parent_account": "Total Expenses",
        }

        result = transformer.transform_account(raw_data)

        assert result["account_name"] == "Operating Expenses"
        assert result["account_type"] == "expense"
        assert result["source_system"] == "rootfi"
        assert result["source_account_id"] == "ACC123"
        assert result["parent_account_id"] == "Total Expenses"
        assert result["account_id"] is not None

    def test_transform_account_deduplication(self, transformer):
        """Test that duplicate accounts are filtered."""
        raw_data = {
            "account_name": "Test Account",
            "account_type": "revenue",
            "source_system": "test",
        }

        result1 = transformer.transform_account(raw_data)
        result2 = transformer.transform_account(raw_data)

        assert result1 is not None
        assert result2 is None  # Duplicate should be filtered
