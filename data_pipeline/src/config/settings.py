"""
Configuration management using Pydantic Settings.
Loads configuration from environment variables and .env file.
"""
from pathlib import Path
from typing import Optional

from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # PostgreSQL Configuration
    postgres_host: str = Field(default="localhost", description="PostgreSQL host")
    postgres_port: int = Field(default=5432, description="PostgreSQL port")
    postgres_db: str = Field(default="financial_data", description="Database name")
    postgres_user: str = Field(default="postgres", description="Database user")
    postgres_password: str = Field(default="", description="Database password")

    # Pipeline Configuration
    chunk_size: int = Field(default=1000, description="Batch processing chunk size")
    log_level: str = Field(default="INFO", description="Logging level")

    # Data Sources
    quickbooks_data_path: str = Field(
        default="data/data_set_1.json", description="Path to QuickBooks data"
    )
    rootfi_data_path: str = Field(
        default="data/data_set_2.json", description="Path to Rootfi data"
    )

    @property
    def postgres_url(self) -> str:
        """Generate PostgreSQL connection URL."""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def project_root(self) -> Path:
        """Get project root directory."""
        return Path(__file__).parent.parent.parent

    @property
    def data_dir(self) -> Path:
        """Get data directory."""
        return self.project_root / "data"

    @property
    def logs_dir(self) -> Path:
        """Get logs directory."""
        return self.project_root / "logs"


# Global settings instance
settings = Settings()
