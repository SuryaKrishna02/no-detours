# evaluation/evaluator.py
from typing import Dict, List, Any
from api.llm_provider import LLMProvider
from app.prompt_templates.system_prompts import EVALUATOR_SYSTEM_PROMPT
from app.prompt_templates.user_prompts import evaluation_prompt

class TravelPlannerEvaluator:
    """Evaluates the quality of generated travel plans."""
    
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
    
    def evaluate_itinerary(self, 
                          itinerary: str, 
                          features: Dict[str, Any], 
                          metrics: List[str] = None) -> Dict[str, float]:
        """
        Evaluate a generated itinerary based on specified metrics.
        
        Args:
            itinerary: The generated travel itinerary
            features: The extracted travel features
            metrics: List of metrics to evaluate (default: relevance, coherence, personalization)
            
        Returns:
            Dict with scores for each metric
        """
        if metrics is None:
            metrics = ["relevance", "coherence", "personalization"]
        
        scores = {}
        
        for metric in metrics:
            score_text = self.llm_provider.generate(
                system_prompt=EVALUATOR_SYSTEM_PROMPT,
                user_prompt=evaluation_prompt(itinerary, features, metric)
            )
            
            try:
                score = float(score_text.strip())
                scores[metric] = score
            except ValueError:
                # If score parsing fails, use a default score
                scores[metric] = 0.5
        
        # Calculate average score across all metrics
        if scores:
            scores["average"] = sum(scores.values()) / len(scores)
        
        return scores