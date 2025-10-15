"""
Reset database and reload all data with standardized categories.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from src.models.base import SessionLocal, engine
from src.models.financial import Base
from src.financial_pipeline import FinancialPipeline
from src.config.logging_config import get_logger

logger = get_logger(__name__)


def clear_all_data():
    """Clear all data from the database."""
    logger.info("clearing_all_data")

    db = SessionLocal()
    try:
        # Delete in order to respect foreign keys
        db.execute(text("TRUNCATE TABLE fact_financials CASCADE"))
        db.execute(text("TRUNCATE TABLE dim_account CASCADE"))
        db.execute(text("TRUNCATE TABLE dim_date CASCADE"))
        db.execute(text("TRUNCATE TABLE dim_source CASCADE"))
        db.execute(text("TRUNCATE TABLE pipeline_runs CASCADE"))
        db.commit()
        logger.info("all_data_cleared")
    except Exception as e:
        logger.error("clear_data_failed", error=str(e))
        db.rollback()
        raise
    finally:
        db.close()


def main():
    """Main execution."""
    print("=" * 60)
    print("DATABASE RESET AND RELOAD WITH STANDARDIZED CATEGORIES")
    print("=" * 60)

    # Confirm action
    response = input("\nThis will DELETE ALL DATA and reload. Continue? (yes/no): ")
    if response.lower() != "yes":
        print("Aborted.")
        return

    try:
        # Step 1: Clear all data
        print("\n[1/2] Clearing all data...")
        clear_all_data()
        print("✓ All data cleared")

        # Step 2: Run pipeline
        print("\n[2/2] Running pipeline with standardized categories...")
        pipeline = FinancialPipeline()
        results = pipeline.run_full_pipeline()

        print("\n" + "=" * 60)
        print("PIPELINE COMPLETED")
        print("=" * 60)
        print(f"QuickBooks: {results['quickbooks']['records_processed']} records processed")
        print(f"Rootfi: {results['rootfi']['records_processed']} records processed")
        print(f"Total: {results['total_records']} records")
        print(f"Failed: {results['total_failed']} records")

        # Show CSV paths if any failed records
        if results['quickbooks'].get('failed_records_csv'):
            print(f"\nQuickBooks failed records: {results['quickbooks']['failed_records_csv']}")
        if results['rootfi'].get('failed_records_csv'):
            print(f"Rootfi failed records: {results['rootfi']['failed_records_csv']}")

        print("\n✓ Database reloaded with standardized categories!")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        logger.error("reset_and_reload_failed", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
