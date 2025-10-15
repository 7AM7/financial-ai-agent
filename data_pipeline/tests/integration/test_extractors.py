"""
Integration tests for data extractors.
Tests against actual data files.
"""
import pytest
from pathlib import Path

from src.config.settings import settings
from data_pipeline.src.extractors.quickbooks_extractor import QuickBooksExtractor
from data_pipeline.src.extractors.rootfi_extractor import RootfiExtractor


class TestQuickBooksExtractor:
    """Integration tests for QuickBooks extractor."""

    @pytest.fixture
    def extractor(self):
        """Create extractor with actual data file."""
        data_path = settings.data_dir / "data_set_1.json"
        if not data_path.exists():
            pytest.skip("QuickBooks data file not found")
        return QuickBooksExtractor(str(data_path))

    def test_validation_success(self, extractor):
        """Test that validation succeeds for valid data."""
        assert extractor.validate() is True

    def test_extraction_yields_records(self, extractor):
        """Test that extraction yields records."""
        extractor.validate()
        records = list(extractor.extract())
        assert len(records) > 0

    def test_extracted_record_structure(self, extractor):
        """Test that extracted records have expected structure."""
        extractor.validate()
        record = next(extractor.extract())

        # Check required fields
        assert "account_name" in record
        assert "account_type" in record
        assert "period_start" in record
        assert "period_end" in record
        assert "amount" in record
        assert "currency" in record
        assert "source_system" in record

        # Check types
        assert isinstance(record["account_name"], str)
        assert isinstance(record["amount"], (int, float))
        assert record["source_system"] == "quickbooks"

    def test_no_zero_amounts(self, extractor):
        """Test that zero-amount records are filtered out."""
        extractor.validate()
        records = list(extractor.extract())
        assert all(record["amount"] != 0.0 for record in records)


class TestRootfiExtractor:
    """Integration tests for Rootfi extractor."""

    @pytest.fixture
    def extractor(self):
        """Create extractor with actual data file."""
        data_path = settings.data_dir / "data_set_2.json"
        if not data_path.exists():
            pytest.skip("Rootfi data file not found")
        return RootfiExtractor(str(data_path))

    def test_validation_success(self, extractor):
        """Test that validation succeeds for valid data."""
        assert extractor.validate() is True

    def test_extraction_yields_records(self, extractor):
        """Test that extraction yields records."""
        extractor.validate()
        records = list(extractor.extract())
        assert len(records) > 0

    def test_extracted_record_structure(self, extractor):
        """Test that extracted records have expected structure."""
        extractor.validate()
        record = next(extractor.extract())

        # Check required fields
        assert "account_name" in record
        assert "account_type" in record
        assert "period_start" in record
        assert "period_end" in record
        assert "amount" in record
        assert "currency" in record
        assert "source_system" in record

        # Check types
        assert isinstance(record["account_name"], str)
        assert isinstance(record["amount"], (int, float))
        assert record["source_system"] == "rootfi"

    def test_account_types_valid(self, extractor):
        """Test that extracted account types are valid."""
        extractor.validate()
        valid_types = {"revenue", "expense", "cogs"}

        records = list(extractor.extract())
        account_types = {record["account_type"] for record in records}

        assert account_types.issubset(valid_types)

    def test_no_zero_amounts(self, extractor):
        """Test that zero-amount records are filtered out."""
        extractor.validate()
        records = list(extractor.extract())
        assert all(record["amount"] != 0.0 for record in records)
