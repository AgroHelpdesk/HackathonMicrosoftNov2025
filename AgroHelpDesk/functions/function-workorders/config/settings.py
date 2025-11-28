"""Settings configuration for Azure Functions using Pydantic.

This module defines configuration settings for the Azure Functions app,
with support for environment variables and Azure Key Vault.
"""

import logging
import os
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from utils.logger import get_logger

logger = get_logger(__name__)


def _get_secret_or_env(secret_name: str, default: Optional[str] = None) -> Optional[str]:
    """Get secret from Key Vault or environment variable.
    
    This function attempts to retrieve secrets from Azure Key Vault first,
    and falls back to environment variables if Key Vault is not configured
    or the secret is not found.
    
    Args:
        secret_name: Name of the secret/environment variable
        default: Default value if not found
        
    Returns:
        Secret value or default
    """
    try:
        # Only import and use Key Vault if USE_KEY_VAULT is enabled
        use_kv = os.getenv("USE_KEY_VAULT", "false").lower() in ("true", "1", "yes")
        
        if use_kv:
            logger.debug(f"Attempting to retrieve secret from Key Vault: {secret_name}")
            from config.keyvault import get_secret_or_env
            
            value = get_secret_or_env(secret_name)
            if value:
                logger.debug(f"Successfully retrieved secret: {secret_name}")
                return value
            
        # Fall back to environment variable
        env_value = os.getenv(secret_name, default)
        if env_value:
            logger.debug(f"Using environment variable for: {secret_name}")
            
        return env_value
        
    except Exception as e:
        logger.warning(f"Error retrieving secret '{secret_name}': {e}")
        return os.getenv(secret_name, default)


class Settings(BaseSettings):
    """Application settings with Key Vault integration."""
    
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Logging configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    
    enable_detailed_logging: bool = Field(
        default=False,
        description="Enable detailed logging for debugging"
    )

    # Key Vault configuration
    use_key_vault: bool = Field(
        default_factory=lambda: os.getenv("USE_KEY_VAULT", "false").lower() in ("true", "1", "yes"),
        description="Enable Azure Key Vault for secrets management"
    )
    
    azure_key_vault_url: Optional[str] = Field(
        default_factory=lambda: _get_secret_or_env("AZURE_KEY_VAULT_URL"),
        description="Azure Key Vault URL",
        alias="AZURE-KEY-VAULT-URL"
    )

    # Cosmos DB configuration
    cosmos_endpoint: str = Field(
        default_factory=lambda: _get_secret_or_env("COSMOS_ENDPOINT", ""),
        description="Azure Cosmos DB endpoint URL",
        alias="COSMOS-ENDPOINT"        
    )
    
    cosmos_key: Optional[str] = Field(
        default_factory=lambda: _get_secret_or_env("COSMOS_KEY"),
        description="Azure Cosmos DB access key",
        alias="COSMOS-KEY"
    )
    
    cosmos_database_name: str = Field(
        default="agrodesk",
        description="Cosmos DB database name"
    )
    
    cosmos_container_name: str = Field(
        default="workorders",
        description="Cosmos DB container name"
    )



    def model_post_init(self, __context) -> None:
        """Post-initialization validation and setup."""
        # Validate required Cosmos DB configuration (but don't fail hard)
        if not self.cosmos_endpoint:
            logger.warning("COSMOS_ENDPOINT is not configured")
            
        if not self.cosmos_key:
            logger.warning("COSMOS_KEY is not configured")

        # Set up logging level
        if self.log_level.upper() in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            logging.getLogger().setLevel(getattr(logging, self.log_level.upper()))
        else:
            logger.warning(f"Invalid log level: {self.log_level}. Using INFO instead.")
            logging.getLogger().setLevel(logging.INFO)

        logger.info("Settings initialized successfully")
        logger.debug(f"Using Key Vault: {self.use_key_vault}")
        logger.debug(f"Cosmos DB endpoint: {self.cosmos_endpoint or 'NOT SET'}")


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create the global settings instance.
    
    Returns:
        Settings instance.
    """
    global _settings
    
    if _settings is None:
        _settings = Settings()
    
    return _settings