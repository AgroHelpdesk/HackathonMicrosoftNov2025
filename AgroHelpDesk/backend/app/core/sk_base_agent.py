"""Base class for Semantic Kernel agents.

This module provides a base class that wraps Semantic Kernel's ChatCompletionAgent
while maintaining compatibility with the existing AgentResponseSchema.
"""

import json
import time
from typing import Any, Dict, Optional

from semantic_kernel import Kernel
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.contents.utils.author_role import AuthorRole

from app.config.kernel_config import get_kernel
from app.schemas.orchestrator_schemas import AgentResponseSchema, AgentType
from app.utils.logger import get_logger

logger = get_logger("sk_base_agent")


class SKBaseAgent:
    """Base class for Semantic Kernel agents.
    
    Provides common functionality for SK-based agents while maintaining
    compatibility with existing AgentResponseSchema.
    """
    
    def __init__(
        self,
        agent_name: str,
        agent_type: AgentType,
        system_prompt: str,
        kernel: Optional[Kernel] = None
    ):
        """Initialize SK base agent.
        
        Args:
            agent_name: Human-readable name of the agent
            agent_type: Type of the agent (from AgentType enum)
            system_prompt: System prompt defining agent behavior
            kernel: Optional kernel instance. If None, uses global kernel.
        """
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.system_prompt = system_prompt
        self.kernel = kernel or get_kernel()
        self.logger = get_logger(f"sk_agent.{agent_name}")
    
    async def process(self, message: str, context: Dict[str, Any]) -> AgentResponseSchema:
        """Process message and return standardized response.
        
        This method wraps the internal processing with timing, logging, and error handling.
        
        Args:
            message: User message to process
            context: Additional context
            
        Returns:
            AgentResponseSchema with execution results
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"Starting processing for {self.agent_name}")
            
            # Call the agent-specific implementation
            data = await self._process_internal(message, context)
            
            execution_time_ms = (time.time() - start_time) * 1000
            
            self.logger.info(
                f"{self.agent_name} completed successfully in {execution_time_ms:.2f}ms"
            )
            
            return AgentResponseSchema(
                agent_name=self.agent_name,
                agent_type=self.agent_type,
                success=True,
                data=data,
                execution_time_ms=execution_time_ms,
                error=None
            )
            
        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            error_msg = str(e)
            
            self.logger.error(
                f"{self.agent_name} failed after {execution_time_ms:.2f}ms: {error_msg}",
                exc_info=True
            )
            
            return AgentResponseSchema(
                agent_name=self.agent_name,
                agent_type=self.agent_type,
                success=False,
                data={},
                execution_time_ms=execution_time_ms,
                error=error_msg
            )
    
    async def _process_internal(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Internal processing method to be implemented by each agent.
        
        Args:
            message: User message to process
            context: Additional context (thread_id, sender_id, etc.)
            
        Returns:
            Dict containing agent-specific response data
        """
        raise NotImplementedError("Subclasses must implement _process_internal")
    
    async def invoke_prompt(
        self,
        user_message: str,
        temperature: float = 0.2,
        max_tokens: int = 512,
        chat_history: Optional[ChatHistory] = None
    ) -> str:
        """Invoke a prompt using Semantic Kernel.
        
        Args:
            user_message: User message to process
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            chat_history: Optional chat history
            
        Returns:
            Response content as string
        """
        # Create chat history if not provided
        if chat_history is None:
            chat_history = ChatHistory()
            chat_history.add_system_message(self.system_prompt)
        
        # Add user message
        chat_history.add_user_message(user_message)
        
        # Get chat completion service - use proper type import
        from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
        from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings
        
        chat_service = self.kernel.get_service(type=ChatCompletionClientBase)
        
        settings = OpenAIChatPromptExecutionSettings(
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Get response
        response = await chat_service.get_chat_message_content(
            chat_history=chat_history,
            settings=settings,
            kernel=self.kernel
        )
        
        return str(response.content) if response.content else ""
    
    async def invoke_structured_prompt(
        self,
        user_message: str,
        temperature: float = 0.1,
        max_tokens: int = 512
    ) -> Dict[str, Any]:
        """Invoke a prompt expecting structured JSON response.
        
        Args:
            user_message: User message to process
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Parsed JSON response as dictionary
        """
        chat_history = ChatHistory()
        chat_history.add_system_message(self.system_prompt)
        chat_history.add_user_message(user_message)
        
        # Get chat completion service - use proper type import
        from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
        from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings
        
        chat_service = self.kernel.get_service(type=ChatCompletionClientBase)
        
        # Use proper response_format as dictionary for JSON mode
        settings = OpenAIChatPromptExecutionSettings(
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"}  # Correct format for JSON mode
        )
        
        response = await chat_service.get_chat_message_content(
            chat_history=chat_history,
            settings=settings,
            kernel=self.kernel
        )
        
        content = str(response.content) if response.content else "{}"
        
        # Parse JSON
        try:
            # Remove markdown code blocks if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            
            return json.loads(content)
        except json.JSONDecodeError as e:
            self.logger.warning(f"Failed to parse JSON response: {e}")
            self.logger.debug(f"Raw content: {content}")
            raise ValueError(f"Invalid JSON response: {e}")
