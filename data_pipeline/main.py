#!/usr/bin/env python3
"""
Main entry point for the financial data ELT pipeline.
"""
import argparse
import sys

from src.config.logging_config import setup_logging, get_logger
from src.models.base import init_db, SessionLocal
from src.models.aggregates import create_aggregate_views, create_indexes_for_performance
from src.financial_pipeline import FinancialPipeline

# Setup logging
setup_logging()
logger = get_logger(__name__)


def init_database():
    """Initialize database tables and views."""
    logger.info("database_initialization_started")
    try:
        # Create tables
        init_db()
        print("✓ Database tables created")

        # Create aggregate views
        db = SessionLocal()
        try:
            create_aggregate_views(db)
            print("✓ Aggregate views created (6 views)")

            create_indexes_for_performance(db)
            print("✓ Performance indexes created")
        finally:
            db.close()

        logger.info("database_initialization_completed")
        print("\n✓ Database initialized successfully")
        print("  - Tables: dim_account, dim_date, dim_source, fact_financials")
        print("  - Views: v_monthly_summary, v_category_performance, v_profit_loss,")
        print("           v_yoy_growth, v_top_accounts, v_trend_analysis")
    except Exception as e:
        logger.error("database_initialization_failed", error=str(e))
        print(f"✗ Database initialization failed: {e}")
        sys.exit(1)


def run_pipeline(source: str = "all"):
    """
    Run the ELT pipeline.

    Args:
        source: Data source to process (quickbooks, rootfi, or all)
    """
    logger.info("pipeline_execution_started", source=source)

    try:
        pipeline = FinancialPipeline()

        if source == "quickbooks":
            stats = pipeline.run_quickbooks_pipeline()
            print(f"\n✓ QuickBooks Pipeline Completed")
            print(f"  Records Processed: {stats['records_processed']}")
            print(f"  Records Failed: {stats['records_failed']}")

        elif source == "rootfi":
            stats = pipeline.run_rootfi_pipeline()
            print(f"\n✓ Rootfi Pipeline Completed")
            print(f"  Records Processed: {stats['records_processed']}")
            print(f"  Records Failed: {stats['records_failed']}")

        elif source == "all":
            stats = pipeline.run_full_pipeline()
            print(f"\n✓ Full Pipeline Completed")

            if stats.get("quickbooks"):
                qb = stats["quickbooks"]
                if "error" not in qb:
                    print(f"\n  QuickBooks:")
                    print(f"    Records: {qb['records_processed']}")
                    print(f"    Failed: {qb['records_failed']}")
                else:
                    print(f"\n  QuickBooks: ERROR - {qb['error']}")

            if stats.get("rootfi"):
                rf = stats["rootfi"]
                if "error" not in rf:
                    print(f"\n  Rootfi:")
                    print(f"    Records: {rf['records_processed']}")
                    print(f"    Failed: {rf['records_failed']}")
                else:
                    print(f"\n  Rootfi: ERROR - {rf['error']}")

            print(f"\n  Total Records: {stats['total_records']}")
            print(f"  Total Failed: {stats['total_failed']}")

        else:
            print(f"✗ Invalid source: {source}")
            sys.exit(1)

        logger.info("pipeline_execution_completed", source=source)

    except Exception as e:
        logger.error("pipeline_execution_failed", error=str(e), source=source)
        print(f"\n✗ Pipeline failed: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Financial Data ELT Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Initialize database
  python main.py init

  # Run full pipeline
  python main.py run

  # Run specific source
  python main.py run --source quickbooks
  python main.py run --source rootfi
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Init command
    subparsers.add_parser("init", help="Initialize database tables")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run ELT pipeline")
    run_parser.add_argument(
        "--source",
        choices=["quickbooks", "rootfi", "all"],
        default="all",
        help="Data source to process (default: all)",
    )

    args = parser.parse_args()

    if args.command == "init":
        init_database()
    elif args.command == "run":
        run_pipeline(source=args.source)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
