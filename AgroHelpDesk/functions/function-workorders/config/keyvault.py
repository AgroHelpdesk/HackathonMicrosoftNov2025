"""Azure Key Vault integration module.

This module provides utilities to retrieve secrets from Azure Key Vault
using managed identity or service principal authentication.
"""

import os
from typing import Optional

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from utils.logger import get_logger

logger = get_logger("config.keyvault")


class KeyVaultClient:
    """Client for interacting with Azure Key Vault."""

    def __init__(self, vault_url: Optional[str] = None):
        """Initialize Key Vault client.

        Args:
            vault_url: Azure Key Vault URL. If not provided, reads from
                      AZURE_KEY_VAULT_URL environment variable.
        """
        self.vault_url = vault_url or os.getenv("AZURE_KEY_VAULT_URL")
        
        if not self.vault_url:
            logger.warning("Azure Key Vault URL not configured. Secrets will not be loaded from Key Vault.")
            self._client = None
            return

        # Validate vault URL format
        if not self.vault_url.startswith("https://"):
            raise ValueError("Key Vault URL must start with https://")

        self._client = self._create_client()
        logger.info(f"Key Vault client initialized for: {self.vault_url}")

    def _create_client(self) -> Optional[SecretClient]:
        """Create and return a SecretClient with appropriate credentials.

        Returns:
            SecretClient instance or None if vault URL is not configured.
        """
        if not self.vault_url:
            return None

        # Use DefaultAzureCredential (supports Managed Identity, Azure CLI, etc.)
        logger.info("Using DefaultAzureCredential for Key Vault (Managed Identity/Azure CLI)")
        credential = DefaultAzureCredential()

        return SecretClient(vault_url=self.vault_url, credential=credential)

    def get_secret(self, secret_name: str, default: Optional[str] = None) -> Optional[str]:
        """Retrieve a secret from Azure Key Vault.

        Args:
            secret_name: Name of the secret to retrieve.
            default: Default value to return if secret is not found or Key Vault is not configured.

        Returns:
            Secret value or default if not found.
        """
        if not self._client:
            logger.debug(f"Key Vault not configured. Using default value for secret: {secret_name}")
            return default

        try:
            secret = self._client.get_secret(secret_name)
            logger.info(f"Successfully retrieved secret: {secret_name}")
            return secret.value
        except Exception as e:
            logger.warning(f"Failed to retrieve secret '{secret_name}' from Key Vault: {e}")
            return default

    def get_secret_or_env(self, secret_name: str) -> Optional[str]:
        """Retrieve a secret from Key Vault or fall back to environment variable.

        This method first tries to get the secret from Key Vault. If that fails
        or Key Vault is not configured, it falls back to reading from environment variable.

        Args:
            secret_name: Name of the secret (same name used in both Key Vault and env vars).

        Returns:
            Secret value from Key Vault or environment variable, or None if not found.
        """
        # Try Key Vault first if enabled
        use_kv = os.getenv("USE_KEY_VAULT", "false").lower() in ("true", "1", "yes")
        
        if use_kv:
            value = self.get_secret(secret_name)
            if value is not None:
                return value
        
        # Fall back to environment variable
        env_value = os.getenv(secret_name)
        if env_value:
            logger.debug(f"Using environment variable for: {secret_name}")
        
        return env_value


# Global Key Vault client instance
_keyvault_client: Optional[KeyVaultClient] = None


def get_keyvault_client() -> KeyVaultClient:
    """Get or create the global Key Vault client instance.

    Returns:
        KeyVaultClient instance.
    """
    global _keyvault_client
    
    if _keyvault_client is None:
        _keyvault_client = KeyVaultClient()
    
    return _keyvault_client


def get_secret(secret_name: str, default: Optional[str] = None) -> Optional[str]:
    """Convenience function to retrieve a secret from Key Vault.

    Args:
        secret_name: Name of the secret to retrieve.
        default: Default value to return if secret is not found.

    Returns:
        Secret value or default if not found.
    """
    client = get_keyvault_client()
    return client.get_secret(secret_name, default)


def get_secret_or_env(secret_name: str) -> Optional[str]:
    """Convenience function to retrieve a secret from Key Vault or environment variable.

    Args:
        secret_name: Name of the secret (same for both Key Vault and env vars).

    Returns:
        Secret value from Key Vault or environment variable, or None if not found.
    """
    client = get_keyvault_client()
    return client.get_secret_or_env(secret_name)