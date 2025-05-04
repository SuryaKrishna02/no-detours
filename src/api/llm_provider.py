"""
api/llm_provider.py

This module provides a unified interface for interacting with different Large Language Model providers.
It currently supports OpenAI and Anthropic APIs with configurable parameters.
"""

import os
import openai
import logging
import anthropic
from dotenv import load_dotenv
from typing import Dict, List, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class LLMProvider:
    """
    Interface for interacting with different LLM providers.
    
    This class abstracts away the differences between various LLM APIs
    (currently OpenAI and Anthropic) and provides a unified interface
    for generating text completions.
    
    Attributes:
        provider (str): The LLM provider name (e.g., "openai", "anthropic").
        model (str): The specific model to use (e.g., "gpt-4", "claude-3-5-sonnet-latest").
        temperature (float): Controls randomness in generation. Higher values mean more random completions.
        max_tokens (int): Maximum number of tokens to generate in the response.
        client: The initialized API client for the selected provider.
    """
    
    def __init__(self, provider: str, model: str, temperature: float = 0.7, max_tokens: int = 4000):
        """
        Initialize the LLM provider interface.
        
        Args:
            provider (str): The LLM provider name (e.g., "openai", "anthropic").
            model (str): The specific model to use (e.g., "gpt-4", "claude-3-5-sonnet-latest").
            temperature (float, optional): Controls randomness in generation. Defaults to 0.7.
            max_tokens (int, optional): Maximum number of tokens to generate. Defaults to 4000.
            
        Raises:
            ValueError: If an unsupported provider is specified.
        """
        self.provider = provider.lower()
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        logger.info(f"Initializing LLMProvider with provider={provider}, model={model}")
        
        # Check for API keys
        if self.provider == "anthropic":
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                logger.warning("ANTHROPIC_API_KEY not found in environment variables")
                
            self.client = anthropic.Anthropic(api_key=api_key)
            
        elif self.provider == "openai":
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                logger.warning("OPENAI_API_KEY not found in environment variables")
                
            self.client = openai.OpenAI(api_key=api_key)
        else:
            logger.error(f"Unsupported LLM provider: {provider}")
            raise ValueError(f"Unsupported LLM provider: {provider}")
    
    def generate(self, 
                 system_prompt: str, 
                 user_prompt: str, 
                 conversation_history: Optional[List[Dict[str, str]]] = None) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            system_prompt (str): The system instructions or context to guide the model's behavior.
            user_prompt (str): The user's input or query.
            conversation_history (Optional[List[Dict[str, str]]], optional): 
                Previous messages in the conversation. Each message should be a dictionary 
                with 'role' and 'content' keys. Defaults to None.
                
        Returns:
            str: The generated response text from the LLM.
            
        Raises:
            Exception: If there's an error during the API call, the error is logged and
                      an error message is returned.
        """
        
        if conversation_history is None:
            conversation_history = []
        
        logger.info(f"Generating response with {self.provider} model {self.model}")
        
        try:
            if self.provider == "anthropic":
                messages = []
                
                # Add conversation history
                for message in conversation_history:
                    messages.append(message)
                
                # Add user message
                messages.append({"role": "user", "content": user_prompt})
                
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    system=system_prompt,
                    messages=messages
                )
                
                return response.content[0].text
                
            elif self.provider == "openai":
                messages = [{"role": "system", "content": system_prompt}]
                
                # Add conversation history
                for message in conversation_history:
                    messages.append(message)
                
                # Add user message
                messages.append({"role": "user", "content": user_prompt})
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                
                return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}", exc_info=True)
            return f"I apologize, but I'm having difficulty generating a response at the moment. Error: {str(e)}"
        
        return "I apologize, but I couldn't generate a response with the current configuration."