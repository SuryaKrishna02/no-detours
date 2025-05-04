"""
modules/guardrail.py

Input validation module for the Travel Planner system. Guards against inappropriate 
or irrelevant user inputs by validating them against travel planning criteria.
"""

import json
from typing import Tuple
from api.llm_provider import LLMProvider

class Guardrail:
    """
    Ensures user inputs are appropriate and relevant to travel planning.
    
    This class provides validation mechanisms to filter out inputs that are either
    unrelated to travel planning or contain inappropriate content, protecting
    the system from misuse and ensuring focused functionality.
    
    Attributes:
        llm_provider (LLMProvider): The language model provider used for validation.
    """
    
    def __init__(self, llm_provider: LLMProvider):
        """
        Initialize the Guardrail with an LLM provider.
        
        Args:
            llm_provider (LLMProvider): The language model provider used for 
                content validation and classification.
        """
        self.llm_provider = llm_provider
    
    def validate_input(self, user_input: str) -> Tuple[bool, str]:
        """
        Validate user input to ensure it's related to travel planning and appropriate.
        
        Sends the user input to an LLM to determine if it's both relevant to travel
        planning and free from harmful, offensive, or inappropriate content.
        
        Args:
            user_input (str): The user's text input to be validated.
            
        Returns:
            Tuple[bool, str]: A tuple containing:
                - bool: True if the input is valid, False otherwise.
                - str: If invalid, contains the reason; empty string if valid.
                
        Example:
            >>> guard = Guardrail(llm_provider)
            >>> is_valid, reason = guard.validate_input("Plan a trip to Paris")
            >>> print(is_valid)
            True
        """
        system_prompt="""
You are a content moderator for a travel planning assistant.
Your task is to determine if the user's input is:
1. Related to travel planning or travel information
2. Appropriate and does not contain harmful, offensive, or inappropriate content

Respond with a JSON object with the following fields:
- is_valid: true if the input passes both checks, false otherwise
- reason: If is_valid is false, provide a brief reason

Provide only the JSON, with no additional text.
"""
        response = self.llm_provider.generate(
            system_prompt=system_prompt,
            user_prompt=user_input
        )
        
        try:
            result = json.loads(response)
            return result.get("is_valid", False), result.get("reason", "Invalid input")
        except json.JSONDecodeError:
            # Fallback in case the model doesn't return valid JSON
            return False, "Failed to validate input"