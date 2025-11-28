"""Azure Communication Services Messages management.

This module provides functions to send messages to chat threads using
the Azure Communication Services SDK.
"""

from typing import Any

from azure.communication.chat import CommunicationTokenCredential
from azure.communication.chat.aio import ChatClient

from app.config import settings
from app.services.acs_threads import _get_or_create_bot_user
from app.utils.logger import get_logger

logger = get_logger("acs_messages")


async def send_message_to_thread(
    thread_id: str, message: str, sender_display_name: str = "AgroHelpDesk Bot"
) -> dict[str, Any]:
    """Send a message to an Azure Communication Services chat thread.

    Args:
        thread_id: The ID of the thread to send the message to
        message: The message content to send
        sender_display_name: Display name for the message sender

    Returns:
        Dictionary containing the message ID and other response data

    Raises:
        Exception: If sending the message fails
    """
    try:
        user_id, access_token = _get_or_create_bot_user()
        
        async with ChatClient(
            settings.ACS_ENDPOINT,
            CommunicationTokenCredential(access_token)
        ) as chat_client:
            chat_thread_client = chat_client.get_chat_thread_client(thread_id)
            
            send_message_result = await chat_thread_client.send_message(
                content=message,
                sender_display_name=sender_display_name,
            )
            
            result = {
                "id": send_message_result,
                "thread_id": thread_id,
            }
            
            logger.info(f"Message sent successfully to thread {thread_id}")
            return result

    except Exception as e:
        logger.exception(f"Failed to send message to thread {thread_id}: {e}")
        raise


async def get_messages(thread_id: str, limit: int = 50) -> list[dict[str, Any]]:
    """Get messages from a chat thread.

    Args:
        thread_id: ID of the chat thread
        limit: Maximum number of messages to retrieve

    Returns:
        List of messages with their content and metadata
    """
    try:
        user_id, access_token = _get_or_create_bot_user()
        
        async with ChatClient(
            settings.ACS_ENDPOINT,
            CommunicationTokenCredential(access_token)
        ) as chat_client:
            chat_thread_client = chat_client.get_chat_thread_client(thread_id)
            
            messages = []
            async for message in chat_thread_client.list_messages():
                messages.append({
                    "id": message.id,
                    "type": message.type,
                    "content": message.content.message if hasattr(message.content, "message") else str(message.content),
                    "sender_display_name": message.sender_display_name,
                    "created_on": message.created_on.isoformat() if message.created_on else None,
                })
                if len(messages) >= limit:
                    break
            
            logger.info(f"Retrieved {len(messages)} messages from thread {thread_id}")
            return messages

    except Exception as e:
        logger.exception(f"Failed to get messages from thread {thread_id}: {e}")
        raise
