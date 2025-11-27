"""Semantic Kernel configuration and initialization.

This module provides the Semantic Kernel instance configured with Azure OpenAI
and all necessary plugins for the AgroHelpDesk system.
"""

from typing import Optional

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("kernel_config")

# Global kernel instance (singleton)
_kernel_instance: Optional[Kernel] = None


def get_kernel() -> Kernel:
    """Get or create the Semantic Kernel instance.
    
    Returns:
        Configured Kernel instance with Azure OpenAI service.
    """
    global _kernel_instance
    
    if _kernel_instance is None:
        logger.info("Initializing Semantic Kernel")
        _kernel_instance = _create_kernel()
        logger.info("Semantic Kernel initialized successfully")
    
    return _kernel_instance


def _create_kernel() -> Kernel:
    """Create and configure a new Kernel instance.
    
    Returns:
        Configured Kernel with Azure OpenAI service.
    """
    kernel = Kernel()
    
    # Configure Azure OpenAI service
    azure_chat_service = AzureChatCompletion(
        deployment_name=settings.OPENAI_DEPLOYMENT,
        endpoint=settings.OPENAI_ENDPOINT,
        api_key=settings.OPENAI_KEY,
        api_version=settings.OPENAI_API_VERSION,
    )
    
    # Add service to kernel
    kernel.add_service(azure_chat_service)
    
    logger.info(
        f"Azure OpenAI service configured: "
        f"deployment={settings.OPENAI_DEPLOYMENT}, "
        f"endpoint={settings.OPENAI_ENDPOINT}"
    )
    
    return kernel


def get_chat_completion_service(kernel: Optional[Kernel] = None) -> ChatCompletionClientBase:
    """Get the chat completion service from the kernel.
    
    Args:
        kernel: Optional kernel instance. If None, uses global kernel.
        
    Returns:
        Chat completion service instance.
    """
    if kernel is None:
        kernel = get_kernel()
    
    service = kernel.get_service(type=ChatCompletionClientBase)
    return service


async def reset_kernel() -> None:
    """Reset the global kernel instance.
    
    Useful for testing or reinitialization.
    """
    global _kernel_instance
    _kernel_instance = None
    logger.info("Kernel instance reset")
