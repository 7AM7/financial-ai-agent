"""
Prompt loader - loads YAML templates and creates PromptTemplate instances.
"""

import yaml
from pathlib import Path
from datetime import datetime
from langchain_core.prompts import PromptTemplate


# Get base directory for prompts
PROMPTS_DIR = Path(__file__).parent


def load_yaml(filename: str) -> dict:
    """Load a YAML file from the prompts directory."""
    filepath = PROMPTS_DIR / filename
    with open(filepath, 'r') as f:
        return yaml.safe_load(f)


def get_current_date_info() -> str:
    """Generate current date context information."""
    now = datetime.now()
    current_quarter = (now.month - 1) // 3 + 1

    return f"""## Current Date Context:
- Today: {now.strftime('%Y-%m-%d')}
- Current Year: {now.year}
- Current Quarter: Q{current_quarter}

**CRITICAL**: When users say "this year", use year = {now.year}
When they say "last year", use year = {now.year - 1}"""


# Load context
context_data = load_yaml('context.yaml')
FINANCIAL_CONTEXT = context_data['financial_context']

# Get dynamic date info
CURRENT_DATE_INFO = get_current_date_info()
CURRENT_YEAR = datetime.now().year


# Load template files
system_data = load_yaml('templates/system.yaml')
write_data = load_yaml('templates/write.yaml')
check_data = load_yaml('templates/check.yaml')
repair_data = load_yaml('templates/repair.yaml')


# Build prompt templates with variable substitution
SYSTEM_PROMPT = system_data['template'].format(
    current_date_info=CURRENT_DATE_INFO
)

WRITE_PROMPT_TEXT = write_data['template'].format(
    current_date_info=CURRENT_DATE_INFO,
    current_year=CURRENT_YEAR
)

CHECK_PROMPT_TEXT = check_data['template'].format(
    financial_context=FINANCIAL_CONTEXT
)

REPAIR_PROMPT_TEXT = repair_data['template']


# Create PromptTemplate instances for LangChain
WRITE_PROMPT = PromptTemplate.from_template(WRITE_PROMPT_TEXT)
CHECK_PROMPT = PromptTemplate.from_template(CHECK_PROMPT_TEXT)
REPAIR_PROMPT = PromptTemplate.from_template(REPAIR_PROMPT_TEXT)
