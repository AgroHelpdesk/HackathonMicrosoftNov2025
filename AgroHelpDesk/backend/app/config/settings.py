"""Application configuration module.

This module manages all configuration settings using Pydantic Settings,
loading values from environment variables and .env file.
Supports Azure Key Vault integration for secure secrets management.

Note: Environment variables can use either HYPHENS (-) for Key Vault compatibility
or UNDERSCORES (_) for Azure App Settings compatibility. Both formats are supported.

When USE_KEY_VAULT is enabled, secrets are automatically retrieved from Azure Key Vault
using Managed Identity authentication, with fallback to environment variables.
"""

import os
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _get_secret_or_env(secret_name: str, default: Optional[str] = None) -> Optional[str]:
    """Get secret from Key Vault or environment variable.
    
    Supports both hyphenated (KEY-NAME) and underscored (KEY_NAME) formats.
    
    If USE_KEY_VAULT is enabled, tries to get from Key Vault first,
    then falls back to environment variable.
    
    Args:
        secret_name: Name of the secret/environment variable
        default: Default value if not found
        
    Returns:
        Secret value or default
    """
    use_kv = os.getenv("USE_KEY_VAULT", "false").lower() in ("true", "1", "yes")
    
    if use_kv:
        try:
            from app.config.keyvault import get_secret_or_env
            # Try hyphenated version for Key Vault
            value = get_secret_or_env(secret_name)
            if value is not None:
                return value
        except Exception as e:
            # If Key Vault fails, fall back to env var
            pass
    
    # Try both formats: hyphenated and underscored
    value = os.getenv(secret_name)  # Try hyphenated first
    if value is None:
        # Try underscored version for Azure App Settings
        value = os.getenv(secret_name.replace("-", "_"))
    
    return value or default


class Settings(BaseSettings):
    """Application settings loaded from environment variables.
    
    All environment variable names use hyphens (-) for consistency with Azure Key Vault.
    """

    # Azure Key Vault (Optional)
    AZURE_KEY_VAULT_URL: Optional[str] = Field(
        default=None, 
        description="Azure Key Vault URL for secrets management",
        alias="AZURE-KEY-VAULT-URL"
    )
    USE_KEY_VAULT: bool = Field(
        default=False, 
        description="Enable Azure Key Vault for secrets retrieval",
        alias="USE-KEY-VAULT"
    )

    # Azure OpenAI
    OPENAI_ENDPOINT: str = Field(
        default_factory=lambda: _get_secret_or_env("OPENAI-ENDPOINT", ""),
        description="Azure OpenAI endpoint URL",
        alias="OPENAI-ENDPOINT"
    )
    OPENAI_KEY: str = Field(
        default_factory=lambda: _get_secret_or_env("OPENAI-KEY", ""),
        description="Azure OpenAI API key",
        alias="OPENAI-KEY"
    )
    OPENAI_DEPLOYMENT: str = Field(
        default_factory=lambda: _get_secret_or_env("OPENAI-DEPLOYMENT", "gpt-4o-mini"),
        description="Azure OpenAI deployment name",
        alias="OPENAI-DEPLOYMENT"
    )
    OPENAI_API_VERSION: str = Field(
        default_factory=lambda: _get_secret_or_env("OPENAI-API-VERSION", "2024-02-15-preview"),
        description="Azure OpenAI API version",
        alias="OPENAI-API-VERSION"
    )

    # Azure Communication Services (ACS)
    ACS_ENDPOINT: str = Field(
        default_factory=lambda: _get_secret_or_env("ACS-ENDPOINT", ""),
        description="Azure Communication Services endpoint URL",
        alias="ACS-ENDPOINT"
    )
    ACS_ACCESS_KEY: str = Field(
        default_factory=lambda: _get_secret_or_env("ACS-ACCESS-KEY", ""),
        description="Azure Communication Services access key",
        alias="ACS-ACCESS-KEY"
    )

    # Azure Cognitive Search (Optional)
    AZURE_SEARCH_ENDPOINT: Optional[str] = Field(
        default_factory=lambda: _get_secret_or_env("AZURE-SEARCH-ENDPOINT"),
        description="Azure Cognitive Search endpoint URL",
        alias="AZURE-SEARCH-ENDPOINT"
    )
    AZURE_SEARCH_KEY: Optional[str] = Field(
        default_factory=lambda: _get_secret_or_env("AZURE-SEARCH-KEY"),
        description="Azure Cognitive Search API key",
        alias="AZURE-SEARCH-KEY"
    )
    AZURE_SEARCH_INDEX_NAME: Optional[str] = Field(
        default_factory=lambda: _get_secret_or_env("AZURE-SEARCH-INDEX-NAME"),
        description="Azure Cognitive Search index name",
        alias="AZURE-SEARCH-INDEX-NAME"
    )

    # Session store (Redis) optional
    REDIS_URL: Optional[str] = Field(
        default_factory=lambda: _get_secret_or_env("REDIS-URL"),
        description="Redis connection URL for session storage",
        alias="REDIS-URL"
    )
    
    # Azure Functions for Work Orders
    FUNCTIONS_URL: Optional[str] = Field(
        default_factory=lambda: _get_secret_or_env("FUNCTIONS-URL", "http://localhost:7071"),
        description="Azure Functions base URL for work order operations",
        alias="FUNCTIONS-URL"
    )
    FUNCTIONS_KEY: Optional[str] = Field(
        default_factory=lambda: _get_secret_or_env("FUNCTIONS-KEY"),
        description="Azure Functions access key for authentication",
        alias="FUNCTIONS-KEY"
    )

    # Application settings
    ENVIRONMENT: str = Field(
        default="development", 
        description="Application environment"
    )
    LOG_LEVEL: str = Field(
        default="INFO", 
        description="Logging level",
        alias="LOG-LEVEL"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
        populate_by_name=True,  # Allow both alias and field name
    )

    @field_validator("OPENAI_ENDPOINT", "ACS_ENDPOINT")
    @classmethod
    def validate_endpoint_url(cls, v: str) -> str:
        """Validate that endpoint URLs are properly formatted."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("Endpoint must be a valid HTTP(S) URL")
        return v.rstrip("/")


# Load settings
settings = Settings()