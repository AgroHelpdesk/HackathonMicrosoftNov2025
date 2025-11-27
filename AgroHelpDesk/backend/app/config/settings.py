"""Application configuration module.

This module manages all configuration settings using Pydantic Settings,
loading values from environment variables and .env file.
Supports Azure Key Vault integration for secure secrets management.

Note: All environment variable names use HYPHENS (-) instead of underscores (_)
to maintain consistency with Azure Key Vault naming requirements.
"""

from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


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
        ..., 
        description="Azure OpenAI endpoint URL",
        alias="OPENAI-ENDPOINT"
    )
    OPENAI_KEY: str = Field(
        ..., 
        description="Azure OpenAI API key",
        alias="OPENAI-KEY"
    )
    OPENAI_DEPLOYMENT: str = Field(
        default="gpt-4o-mini", 
        description="Azure OpenAI deployment name",
        alias="OPENAI-DEPLOYMENT"
    )
    OPENAI_API_VERSION: str = Field(
        default="2024-02-15-preview", 
        description="Azure OpenAI API version",
        alias="OPENAI-API-VERSION"
    )

    # Azure Communication Services (ACS)
    ACS_ENDPOINT: str = Field(
        ..., 
        description="Azure Communication Services endpoint URL",
        alias="ACS-ENDPOINT"
    )
    ACS_ACCESS_KEY: str = Field(
        ..., 
        description="Azure Communication Services access key",
        alias="ACS-ACCESS-KEY"
    )

    # Azure Cognitive Search (Optional)
    AZURE_SEARCH_ENDPOINT: Optional[str] = Field(
        default=None, 
        description="Azure Cognitive Search endpoint URL",
        alias="AZURE-SEARCH-ENDPOINT"
    )
    AZURE_SEARCH_KEY: Optional[str] = Field(
        default=None, 
        description="Azure Cognitive Search API key",
        alias="AZURE-SEARCH-KEY"
    )
    AZURE_SEARCH_INDEX_NAME: Optional[str] = Field(
        default=None, 
        description="Azure Cognitive Search index name",
        alias="AZURE-SEARCH-INDEX"
    )

    # Session store (Redis) optional
    REDIS_URL: Optional[str] = Field(
        default=None, 
        description="Redis connection URL for session storage",
        alias="REDIS-URL"
    )
    
    # Azure Functions for Work Orders
    FUNCTIONS_URL: Optional[str] = Field(
        default="http://localhost:7071",
        description="Azure Functions base URL for work order operations",
        alias="FUNCTIONS-URL"
    )
    FUNCTIONS_KEY: Optional[str] = Field(
        default=None,
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