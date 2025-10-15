"""
Account Category Standardization.
Maps messy account categories to a clean, standardized set.
"""
from typing import Optional
import re


# Standard category taxonomy (10 main categories)
STANDARD_CATEGORIES = {
    "Revenue": "Revenue",
    "Cost of Goods Sold": "Cost of Goods Sold",
    "Payroll & Compensation": "Payroll & Compensation",
    "Marketing & Advertising": "Marketing & Advertising",
    "Technology & IT": "Technology & IT",
    "Professional Services": "Professional Services",
    "Travel & Entertainment": "Travel & Entertainment",
    "Facilities & Operations": "Facilities & Operations",
    "Office & Administrative": "Office & Administrative",
    "Research & Development": "Research & Development",
    "Depreciation & Amortization": "Depreciation & Amortization",
    "Taxes & Fees": "Taxes & Fees",
    "Other Expenses": "Other Expenses",
}


# Keyword-based mapping rules (order matters - most specific first)
CATEGORY_MAPPINGS = {
    "Revenue": [
        "revenue", "sales", "income", "professional income",
        "business revenue", "service_division", "Sales & Revenue"
    ],
    "Cost of Goods Sold": [
        "cogs", "cost of goods", "material_cost", "material cost",
        "shipping_expense", "shipping", "freight", "material_cost"
    ],
    "Payroll & Compensation": [
        "payroll", "salary", "salaries", "wages", "compensation",
        "labor_expense", "labor expense", "employee", "gratuity",
        "vacation payout", "contribution to fund", "incentive",
        "hiring cost", "hiring", "alc"
    ],
    "Marketing & Advertising": [
        "marketing", "advertising", "advertisement", "promotion",
        "marketing_expense"
    ],
    "Technology & IT": [
        "technology_expense", "technology", "software", "it", "computer",
        "hosting", "cloud", "saas", "internet", "network", "connectivity",
        "application service", "secured storage"
    ],
    "Professional Services": [
        "professional_fee", "professional", "consulting", "legal",
        "accounting", "consultant", "audit", "license", "licensing",
        "fts", "payment to reviewers", "processing fee"
    ],
    "Travel & Entertainment": [
        "travel_expense", "travel", "trip", "entertainment_expense",
        "entertainment", "meal_expense", "meal", "hotel", "flight",
        "personnel travel", "accommodation", "transportation",
        "trip expense", "trip insurance"
    ],
    "Facilities & Operations": [
        "facility_cost", "facility", "facilities", "rent", "lease",
        "utilities", "utility_expense", "utility", "maintenance",
        "building", "operations_expense", "operations", "cleaning",
        "workplace equipment", "leasing"
    ],
    "Office & Administrative": [
        "office_expense", "office", "supplies", "stationery",
        "communication_expense", "communication", "telephone",
        "correspondence", "administrative", "admin", "equipment_expense",
        "equipment", "import duty", "additional expenses", "fees and memberships",
        "membership", "insurance_expense", "insurance"
    ],
    "Research & Development": [
        "research", "development", "r&d", "rd_", "innovation",
        "rd_labor_expense", "rd_labor", "rd_contractor_fee", "rd_contractor",
        "rd_equipment", "rd_supplies", "rd_expense"
    ],
    "Depreciation & Amortization": [
        "depreciation_expense", "depreciation", "amortization"
    ],
    "Taxes & Fees": [
        "tax_expense", "tax", "taxes", "duty", "banking_expense",
        "bank", "financial institution charges", "fee for"
    ],
}


class CategoryMapper:
    """Maps account names and categories to standardized categories."""

    def __init__(self):
        """Initialize the category mapper."""
        self._compiled_patterns = self._compile_patterns()

    def _compile_patterns(self) -> dict[str, list[re.Pattern]]:
        """Compile regex patterns for efficient matching."""
        patterns = {}
        for category, keywords in CATEGORY_MAPPINGS.items():
            patterns[category] = [
                # Don't use word boundaries - just match the keyword anywhere
                re.compile(re.escape(keyword), re.IGNORECASE)
                for keyword in keywords
            ]
        return patterns

    def map_category(
        self,
        account_name: str,
        account_type: str,
        existing_category: Optional[str] = None
    ) -> str:
        """
        Map an account to a standardized category.

        Args:
            account_name: Name of the account
            account_type: Type (revenue, expense, cogs)
            existing_category: Existing category or parent account name

        Returns:
            Standardized category name
        """
        # Revenue accounts always map to Revenue
        if account_type == "revenue":
            return "Revenue"

        # COGS accounts always map to Cost of Goods Sold
        if account_type == "cogs":
            return "Cost of Goods Sold"

        # Combine account name and existing category/parent for matching
        # Account name gets higher priority, so put it first
        search_text = f"{account_name} {existing_category or ''}".lower()

        # Try to match against patterns
        # Check account name first (more specific)
        for category, patterns in self._compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(account_name.lower()):
                    return category

        # Check combined text (account name + parent/category)
        for category, patterns in self._compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(search_text):
                    return category

        # Default to Other Expenses for unmatched expense accounts
        return "Other Expenses"

    def validate_category(self, category: str) -> bool:
        """
        Check if a category is in the standard set.

        Args:
            category: Category to validate

        Returns:
            True if valid, False otherwise
        """
        return category in STANDARD_CATEGORIES


# Singleton instance
_mapper = CategoryMapper()


def map_account_category(
    account_name: str,
    account_type: str,
    existing_category: Optional[str] = None
) -> str:
    """
    Convenience function to map account to standardized category.

    Args:
        account_name: Name of the account
        account_type: Type (revenue, expense, cogs)
        existing_category: Existing category (if any)

    Returns:
        Standardized category name
    """
    return _mapper.map_category(account_name, account_type, existing_category)


def get_standard_categories() -> list[str]:
    """Get list of all standard categories."""
    return list(STANDARD_CATEGORIES.keys())
