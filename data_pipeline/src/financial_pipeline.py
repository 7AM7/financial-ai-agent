"""
Simplified Financial Data Pipeline.
Clean ETL process for QuickBooks and Rootfi data into star schema.
"""
import csv
import uuid
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List

from src.config.logging_config import get_logger
from src.config.settings import settings
from src.models.base import SessionLocal
from src.models.financial import FinancialFact, PipelineRun
from src.extractors.quickbooks_extractor import QuickBooksExtractor
from src.extractors.rootfi_extractor import RootfiExtractor
from src.extractors.base import BaseExtractor
from src.loaders.dimension_loader import DimensionLoader
from src.transformers.financial_transformer import FinancialTransformer

logger = get_logger(__name__)


class FinancialPipeline:
    """
    Simplified ETL pipeline for financial data.
    Loads data into star schema for AI/ML queries.
    """

    def __init__(self):
        """Initialize pipeline components."""
        self.transformer = FinancialTransformer()
        self.quickbooks_extractor = QuickBooksExtractor(settings.quickbooks_data_path)
        self.rootfi_extractor = RootfiExtractor(settings.rootfi_data_path)
        self.failed_records: List[Dict[str, Any]] = []

    def _initialize_date_dimension(self, db_session) -> None:
        """Pre-populate date dimension for the data range."""
        logger.info("initializing_date_dimension")

        # Date range from 2020 to 2026 (covers all data)
        start_date = date(2020, 1, 1)
        end_date = date(2026, 12, 31)

        dim_loader = DimensionLoader(db_session)
        dim_loader.load_date_dimension(start_date, end_date)

    def _load_facts_batch(
        self, db_session, dim_loader: DimensionLoader, facts: list[Dict[str, Any]]
    ) -> int:
        """
        Load a batch of facts into the fact table.

        Args:
            db_session: Database session
            dim_loader: Dimension loader instance
            facts: List of fact dictionaries

        Returns:
            Number of facts loaded
        """
        fact_objects = []

        for fact_data in facts:
            try:
                # Get dimension keys
                account_key = dim_loader.upsert_account(
                    account_id=fact_data["account_id"],
                    account_name=fact_data["account_name"],
                    account_type=fact_data["account_type"],
                    account_category=fact_data.get("account_category"),
                    parent_account_name=fact_data.get("parent_account"),
                    is_parent=False,
                    source_system=fact_data["source_system"],
                    source_account_id=fact_data.get("source_account_id"),
                )

                period_start_key = dim_loader.get_date_key(fact_data["period_start"])
                period_end_key = dim_loader.get_date_key(fact_data["period_end"])
                source_key = dim_loader.get_or_create_source(
                    fact_data["source_system"],
                    description=f"{fact_data['source_system'].title()} Data Source",
                )

                # Extract temporal fields for denormalization
                period_start = fact_data["period_start"]
                year = period_start.year
                quarter = (period_start.month - 1) // 3 + 1
                month = period_start.month
                year_quarter = f"{year}-Q{quarter}"

                # Create fact object
                fact = FinancialFact(
                    account_key=account_key,
                    period_start_key=period_start_key,
                    period_end_key=period_end_key,
                    source_key=source_key,
                    amount=fact_data["amount"],
                    currency=fact_data.get("currency", "USD"),
                    year=year,
                    quarter=quarter,
                    month=month,
                    year_quarter=year_quarter,
                    source_record_id=fact_data.get("source_record_id"),
                )

                fact_objects.append(fact)

            except Exception as e:
                logger.error(
                    "fact_creation_failed",
                    error=str(e),
                    account=fact_data.get("account_name"),
                )
                continue

        # Bulk insert
        if fact_objects:
            db_session.bulk_save_objects(fact_objects)
            db_session.commit()
            logger.info("facts_batch_loaded", count=len(fact_objects))

        return len(fact_objects)

    def _save_failed_records(self, source_name: str, run_id: str) -> str:
        """
        Save failed records to CSV for debugging.

        Args:
            source_name: Source system name
            run_id: Pipeline run ID

        Returns:
            Path to the CSV file
        """
        if not self.failed_records:
            return None

        # Create output directory
        output_dir = Path("output/failed_records")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = output_dir / f"failed_{source_name}_{timestamp}_{run_id[:8]}.csv"

        # Write to CSV
        with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
            if self.failed_records:
                fieldnames = self.failed_records[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.failed_records)

        logger.info("failed_records_saved", path=str(csv_path), count=len(self.failed_records))
        return str(csv_path)

    def run_pipeline(self, extractor: BaseExtractor, source_name: str) -> Dict[str, Any]:
        """
        Run pipeline for any data source.

        Args:
            extractor: Data extractor (QuickBooks or Rootfi)
            source_name: Source system name

        Returns:
            Pipeline run statistics
        """
        run_id = str(uuid.uuid4())
        db_session = SessionLocal()

        # Reset failed records for this run
        self.failed_records = []

        logger.info(f"{source_name}_pipeline_started", run_id=run_id)

        try:
            # Create run record
            run = PipelineRun(
                run_id=run_id,
                source_system=source_name,
                status="started",
                started_at=datetime.utcnow(),
            )
            db_session.add(run)
            db_session.commit()

            # Initialize dimensions
            self._initialize_date_dimension(db_session)
            dim_loader = DimensionLoader(db_session)

            # Extract and load
            extractor.validate()
            batch = []
            total_processed = 0
            total_failed = 0

            for raw_record in extractor.extract():
                try:
                    # Transform (includes standardized category mapping)
                    transformed = self.transformer.transform_transaction(raw_record)
                    batch.append(transformed)

                    # Load in batches
                    if len(batch) >= settings.chunk_size:
                        loaded = self._load_facts_batch(db_session, dim_loader, batch)
                        total_processed += loaded
                        total_failed += len(batch) - loaded
                        batch = []

                except Exception as e:
                    error_msg = str(e)
                    logger.error(f"{source_name}_record_failed", error=error_msg)

                    # Capture failed record for CSV
                    failed_record = {
                        "source_system": source_name,
                        "account_name": raw_record.get("account_name", "N/A"),
                        "account_type": raw_record.get("account_type", "N/A"),
                        "parent_account": raw_record.get("parent_account", "N/A"),
                        "period_start": raw_record.get("period_start", "N/A"),
                        "period_end": raw_record.get("period_end", "N/A"),
                        "amount": raw_record.get("amount", 0),
                        "currency": raw_record.get("currency", "N/A"),
                        "error_message": error_msg,
                        "error_type": type(e).__name__,
                    }
                    self.failed_records.append(failed_record)
                    total_failed += 1

            # Load remaining
            if batch:
                loaded = self._load_facts_batch(db_session, dim_loader, batch)
                total_processed += loaded
                total_failed += len(batch) - loaded

            # Update run record
            run.status = "completed"
            run.records_processed = total_processed
            run.records_failed = total_failed
            run.completed_at = datetime.utcnow()
            db_session.commit()

            # Save failed records to CSV
            failed_csv_path = self._save_failed_records(source_name, run_id)

            stats = {
                "run_id": run_id,
                "source": source_name,
                "records_processed": total_processed,
                "records_failed": total_failed,
                "failed_records_csv": failed_csv_path,
            }

            logger.info(f"{source_name}_pipeline_completed", **stats)
            return stats

        except Exception as e:
            logger.error(f"{source_name}_pipeline_failed", error=str(e))
            run.status = "failed"
            run.error_message = str(e)
            run.completed_at = datetime.utcnow()
            db_session.commit()

            # Save any failed records captured before the error
            self._save_failed_records(source_name, run_id)
            raise
        finally:
            db_session.close()

    def run_quickbooks_pipeline(self) -> Dict[str, Any]:
        """Run QuickBooks data pipeline."""
        return self.run_pipeline(self.quickbooks_extractor, "quickbooks")

    def run_rootfi_pipeline(self) -> Dict[str, Any]:
        """Run Rootfi data pipeline."""
        return self.run_pipeline(self.rootfi_extractor, "rootfi")

    def run_full_pipeline(self) -> Dict[str, Any]:
        """
        Run complete pipeline for all sources.

        Returns:
            Combined pipeline statistics
        """
        logger.info("full_pipeline_started")

        results = {
            "quickbooks": None,
            "rootfi": None,
            "total_records": 0,
            "total_failed": 0,
        }

        # Run QuickBooks
        try:
            qb_stats = self.run_quickbooks_pipeline()
            results["quickbooks"] = qb_stats
            results["total_records"] += qb_stats["records_processed"]
            results["total_failed"] += qb_stats["records_failed"]
        except Exception as e:
            logger.error("quickbooks_error", error=str(e))
            results["quickbooks"] = {"error": str(e)}

        # Run Rootfi
        try:
            rf_stats = self.run_rootfi_pipeline()
            results["rootfi"] = rf_stats
            results["total_records"] += rf_stats["records_processed"]
            results["total_failed"] += rf_stats["records_failed"]
        except Exception as e:
            logger.error("rootfi_error", error=str(e))
            results["rootfi"] = {"error": str(e)}

        logger.info("full_pipeline_completed", **results)
        return results
