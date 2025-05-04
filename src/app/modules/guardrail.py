# app/modules/guardrail.py
import json
from typing import Tuple
from api.llm_provider import LLMProvider

class Guardrail:
    """Ensures user inputs are appropriate and relevant to travel planning."""
    
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
    
    def validate_input(self, user_input: str) -> Tuple[bool, str]:
        """
        Validate user input to ensure it's related to travel planning and appropriate.
        
        Args:
            user_input: The user's text input
            
        Returns:
            Tuple of (is_valid, reason_if_invalid)
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