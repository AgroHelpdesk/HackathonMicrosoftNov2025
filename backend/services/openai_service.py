"""
Azure OpenAI Service
Handles communication with Azure OpenAI for chat completions
"""

import os
import logging
from typing import List, Dict, Any, Optional
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service for interacting with Azure OpenAI"""
    
    def __init__(self):
        """Initialize Azure OpenAI client"""
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        
        if not self.endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT environment variable is required")
        
        # Use Azure CLI credentials
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(),
            "https://cognitiveservices.azure.com/.default"
        )
        
        self.client = AzureOpenAI(
            azure_endpoint=self.endpoint,
            azure_ad_token_provider=token_provider,
            api_version=self.api_version
        )
        
        logger.info(f"OpenAI Service initialized with deployment: {self.deployment}")
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> str:
        """
        Get chat completion from Azure OpenAI
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
            **kwargs: Additional parameters for the API
            
        Returns:
            Generated response text
        """
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error in chat completion: {e}")
            raise
    
    def chat_completion_with_json(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        **kwargs
    ) -> str:
        """
        Get chat completion with JSON response format
        
        Args:
            messages: List of message dicts
            temperature: Sampling temperature
            **kwargs: Additional parameters
            
        Returns:
            JSON formatted response
        """
        return self.chat_completion(
            messages=messages,
            temperature=temperature,
            response_format={"type": "json_object"},
            **kwargs
        )
