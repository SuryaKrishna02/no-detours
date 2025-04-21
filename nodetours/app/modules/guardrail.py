# app/modules/guardrail.py
import json
from typing import Dict, Any, Tuple
from api.llm_provider import LLMProvider
from app.prompt_templates.system_prompts import GUARDRAIL_SYSTEM_PROMPT

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
        response = self.llm_provider.generate(
            system_prompt=GUARDRAIL_SYSTEM_PROMPT,
            user_prompt=user_input
        )
        
        try:
            result = json.loads(response)
            return result.get("is_valid", False), result.get("reason", "Invalid input")
        except json.JSONDecodeError:
            # Fallback in case the model doesn't return valid JSON
            return False, "Failed to validate input"