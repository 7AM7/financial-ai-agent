"""
Backend configuration.
Reuses settings from the data pipeline.
"""
from typing import Optional
from pydantic import model_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class BackendSettings(BaseSettings):
    """Backend-specific settings."""
    host: str = "0.0.0.0"
    port: int = 8000

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "financial_data"
    postgres_user: str = "postgres"
    postgres_password: str = ""

    # LLM Configuration
    model: str = "gpt-4o-mini"
    model_provider: str = "azure_openai"  # "openai" or "azure_openai"
    api_key: str = ""

    # Azure OpenAI specific (required when model_provider=azure_openai)
    azure_endpoint: Optional[str] = None
    azure_deployment: Optional[str] = None
    openai_api_version: Optional[str] = "2025-03-01-preview"

    @model_validator(mode='after')
    def validate_provider_config(self):
        """Validate that required fields are present for the selected provider."""
        if self.model_provider == "azure_openai":
            if not self.azure_endpoint:
                raise ValueError(
                    "AZURE_ENDPOINT is required when MODEL_PROVIDER=azure_openai"
                )
            if not self.azure_deployment:
                raise ValueError(
                    "AZURE_DEPLOYMENT is required when MODEL_PROVIDER=azure_openai"
                )
            if not self.openai_api_version:
                raise ValueError(
                    "OPENAI_API_VERSION is required when MODEL_PROVIDER=azure_openai"
                )
        elif self.model_provider == "openai":
            # OpenAI only requires API key and model
            pass
        else:
            raise ValueError(
                f"Invalid MODEL_PROVIDER: {self.model_provider}. "
                f"Must be 'openai' or 'azure_openai'"
            )

        if not self.api_key:
            raise ValueError("API_KEY is required")

        return self

    @property
    def postgres_url(self) -> str:
        """Generate PostgreSQL connection URL."""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = BackendSettings()
