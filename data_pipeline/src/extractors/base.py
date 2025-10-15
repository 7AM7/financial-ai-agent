"""
Base extractor interface for data sources.
"""
from abc import ABC, abstractmethod
from typing import Generator, Any, Dict


class BaseExtractor(ABC):
    """Abstract base class for data extractors."""

    def __init__(self, source_path: str):
        """
        Initialize extractor.

        Args:
            source_path: Path to data source file
        """
        self.source_path = source_path

    @abstractmethod
    def extract(self) -> Generator[Dict[str, Any], None, None]:
        """
        Extract data from source and yield records.

        Yields:
            Dictionary containing extracted record data
        """
        pass

    @abstractmethod
    def validate(self) -> bool:
        """
        Validate data source format and structure.

        Returns:
            True if validation passes, raises exception otherwise
        """
        pass
