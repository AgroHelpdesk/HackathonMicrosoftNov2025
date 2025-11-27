"""Azure Communication Services Threads management.

This module provides functions to create and manage chat threads using
the Azure Communication Services SDK with proper token-based authentication.
"""

from typing import Any

from azure.communication.chat import CommunicationTokenCredential
from azure.communication.chat.aio import ChatClient
from azure.communication.identity import CommunicationIdentityClient
from azure.core.credentials import AzureKeyCredential

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("acs_threads")

# Cache for bot user identity and token
_bot_user_id: str | None = None
_bot_access_token: str | None = None


def _get_or_create_bot_user() -> tuple[str, str]:
    """Get or create a bot user identity with access token.
    
    Returns:
        Tuple of (user_id, access_token)
    """
    global _bot_user_id, _bot_access_token
    
    if _bot_user_id and _bot_access_token:
        return _bot_user_id, _bot_access_token
    
    # Create identity client
    identity_client = CommunicationIdentityClient(
        settings.ACS_ENDPOINT,
        AzureKeyCredential(settings.ACS_ACCESS_KEY)
    )
    
    # Create user and get token
    user = identity_client.create_user()
    token_response = identity_client.get_token(user, scopes=["chat"])
    
    _bot_user_id = user.properties["id"]
    _bot_access_token = token_response.token
    
    logger.info(f"Created bot user: {_bot_user_id}")
    return _bot_user_id, _bot_access_token


async def create_thread(topic: str = "AgroHelpDesk Chat") -> dict[str, Any]:
    """Create a new chat thread in Azure Communication Services.

    Args:
        topic: Topic/title for the chat thread

    Returns:
        Dictionary containing thread information including thread ID

    Raises:
        Exception: If thread creation fails
    """
    try:
        user_id, access_token = _get_or_create_bot_user()
        
        async with ChatClient(
            settings.ACS_ENDPOINT,
            CommunicationTokenCredential(access_token)
        ) as chat_client:
            create_chat_thread_result = await chat_client.create_chat_thread(topic)
            chat_thread = create_chat_thread_result.chat_thread
            
            result = {
                "id": chat_thread.id,
                "topic": chat_thread.topic,
                "created_on": chat_thread.created_on.isoformat() if chat_thread.created_on else None,
            }
            
            logger.info(f"Thread created successfully: {chat_thread.id}")
            return result

    except Exception as e:
        logger.exception(f"Failed to create thread: {e}")
        raise


async def get_thread(thread_id: str) -> dict[str, Any]:
    """Get information about a specific chat thread.

    Args:
        thread_id: The ID of the thread to retrieve

    Returns:
        Dictionary containing thread information

    Raises:
        Exception: If thread retrieval fails
    """
    try:
        user_id, access_token = _get_or_create_bot_user()
        
        async with ChatClient(
            settings.ACS_ENDPOINT,
            CommunicationTokenCredential(access_token)
        ) as chat_client:
            chat_thread_client = chat_client.get_chat_thread_client(thread_id)
            properties = await chat_thread_client.get_properties()
            
            result = {
                "id": properties.id,
                "topic": properties.topic,
                "created_on": properties.created_on.isoformat() if properties.created_on else None,
            }
            
            logger.info(f"Thread retrieved: {thread_id}")
            return result

    except Exception as e:
        logger.exception(f"Failed to get thread {thread_id}: {e}")
        raise


async def delete_thread(thread_id: str) -> bool:
    """Delete/close a chat thread in Azure Communication Services.

    Args:
        thread_id: The ID of the thread to delete

    Returns:
        True if deletion was successful

    Raises:
        Exception: If thread deletion fails
    """
    try:
        user_id, access_token = _get_or_create_bot_user()
        
        async with ChatClient(
            settings.ACS_ENDPOINT,
            CommunicationTokenCredential(access_token)
        ) as chat_client:
            await chat_client.delete_chat_thread(thread_id)
            
            logger.info(f"Thread deleted successfully: {thread_id}")
            return True

    except Exception as e:
        logger.exception(f"Failed to delete thread {thread_id}: {e}")
        raise
