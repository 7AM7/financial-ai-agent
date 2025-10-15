"""
Prompt templates for the Financial AI Agent.
Loaded from YAML files in the templates/ directory.
"""

from src.agent.prompts.loader import (
    SYSTEM_PROMPT,
    WRITE_PROMPT,
    CHECK_PROMPT,
    REPAIR_PROMPT,
)

__all__ = [
    "SYSTEM_PROMPT",
    "WRITE_PROMPT",
    "CHECK_PROMPT",
    "REPAIR_PROMPT",
]
