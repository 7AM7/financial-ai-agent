"""
Recreate database views with the updated schema.
Drops old v_top_accounts and creates two new views.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.base import SessionLocal
from src.models.aggregates import create_aggregate_views
from src.config.logging_config import get_logger

logger = get_logger(__name__)


def main():
    """Recreate all views."""
    print("=" * 60)
    print("RECREATING DATABASE VIEWS")
    print("=" * 60)

    db = SessionLocal()
    try:
        print("\n[1/1] Creating/updating all views...")
        create_aggregate_views(db)
        print("✓ All views created successfully")

        print("\n" + "=" * 60)
        print("VIEWS CREATED")
        print("=" * 60)
        print("✓ v_monthly_summary")
        print("✓ v_category_performance")
        print("✓ v_profit_loss")
        print("✓ v_yoy_growth")
        print("✓ v_top_accounts_yearly (NEW - no duplicates)")
        print("✓ v_top_accounts_quarterly (NEW - quarterly rankings)")
        print("✓ v_trend_analysis")
        print("✓ v_ai_financial_data")
        print("\n✓ Old v_top_accounts view removed")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        logger.error("view_recreation_failed", error=str(e))
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
