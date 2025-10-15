"""
LLM Provider Manager - Centralized LLM initialization supporting multiple providers.

Supports:
- OpenAI (direct API)
- Azure OpenAI (Azure-hosted OpenAI)
"""
import logging
from typing import Optional, Dict, Any, Union
from langchain_openai import AzureChatOpenAI, ChatOpenAI

logger = logging.getLogger(__name__)

_llm_instance: Optional[Union[AzureChatOpenAI, ChatOpenAI]] = None


class ProviderError(Exception):
    """Raised when provider configuration is invalid."""
    pass


def get_llm(
    model: Optional[str] = None,
    provider: Optional[str] = None,
    api_key: Optional[str] = None,
    **kwargs
) -> Union[AzureChatOpenAI, ChatOpenAI]:
    """
    Get or create LLM instance based on provider configuration.

    Args:
        model: Model name (e.g., "gpt-4o-mini")
        provider: Provider name ("openai" or "azure_openai")
        api_key: API key for the provider
        **kwargs: Additional arguments passed to the client

    Returns:
        Configured LLM instance (AzureChatOpenAI or ChatOpenAI)

    Raises:
        ProviderError: If configuration is invalid

    Examples:
        # OpenAI
        llm = get_llm(
            model="gpt-4o-mini",
            provider="openai",
            api_key="sk-..."
        )

        # Azure OpenAI
        llm = get_llm(
            model="gpt-4o-mini",
            provider="azure_openai",
            api_key="azure-key",
            azure_endpoint="https://....openai.azure.com/",
            azure_deployment="gpt-4o-mini",
            api_version="2025-03-01-preview"
        )
    """
    global _llm_instance

    # Return cached instance if already initialized
    if _llm_instance is not None:
        return _llm_instance

    # Load settings if not provided
    if model is None or provider is None or api_key is None:
        from src.config import settings
        model = model or settings.model
        provider = provider or settings.model_provider
        api_key = api_key or settings.api_key

        # Load provider-specific settings
        if provider == "azure_openai":
            kwargs.setdefault("azure_endpoint", settings.azure_endpoint)
            kwargs.setdefault("azure_deployment", settings.azure_deployment)
            kwargs.setdefault("api_version", settings.openai_api_version)

    # Validate provider
    if provider not in ["openai", "azure_openai"]:
        raise ProviderError(
            f"Unsupported provider: {provider}. "
            f"Supported providers: 'openai', 'azure_openai'"
        )

    # Validate required fields
    if not api_key:
        raise ProviderError("API_KEY is required")

    # Initialize LLM based on provider
    try:
        logger.info(f"Initializing LLM: provider={provider}, model={model}")

        if provider == "azure_openai":
            # Validate Azure-specific fields
            if not kwargs.get("azure_endpoint"):
                raise ProviderError("AZURE_ENDPOINT is required when MODEL_PROVIDER=azure_openai")
            if not kwargs.get("azure_deployment"):
                raise ProviderError("AZURE_DEPLOYMENT is required when MODEL_PROVIDER=azure_openai")
            if not kwargs.get("api_version"):
                raise ProviderError("OPENAI_API_VERSION is required when MODEL_PROVIDER=azure_openai")

            _llm_instance = AzureChatOpenAI(
                azure_deployment=kwargs["azure_deployment"],
                azure_endpoint=kwargs["azure_endpoint"],
                api_version=kwargs["api_version"],
                api_key=api_key,
                **{k: v for k, v in kwargs.items() if k not in ["azure_deployment", "azure_endpoint", "api_version"]}
            )
        else:  # openai
            _llm_instance = ChatOpenAI(
                model=model,
                api_key=api_key,
                **kwargs
            )

        logger.info(f"LLM initialized successfully: {provider}/{model}")
        return _llm_instance

    except Exception as e:
        logger.error(f"Failed to initialize LLM: {e}")
        raise ProviderError(f"Failed to initialize LLM: {e}")


def reset_llm() -> None:
    """
    Reset the cached LLM instance.

    Useful for testing or when configuration changes.
    """
    global _llm_instance
    _llm_instance = None
    logger.info("LLM instance reset")


def get_provider_info() -> Dict[str, Any]:
    """
    Get information about the current LLM provider configuration.

    Returns:
        Dictionary with provider details
    """
    from src.config import settings

    info = {
        "provider": settings.model_provider,
        "model": settings.model,
        "initialized": _llm_instance is not None,
    }

    if settings.model_provider == "azure_openai":
        info["azure_endpoint"] = settings.azure_endpoint
        info["azure_deployment"] = settings.azure_deployment
        info["api_version"] = settings.openai_api_version

    return info
