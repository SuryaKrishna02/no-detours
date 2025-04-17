# prompt_engineering/prompt_optimizer.py
import json
from typing import Dict, List, Any
from api.llm_provider import LLMProvider

class PromptOptimizer:
    """Optimizes prompts through automated prompt engineering."""
    
    def __init__(self, llm_provider: LLMProvider, seed_prompt: str, evaluation_dataset: List[Dict[str, Any]]):
        self.llm_provider = llm_provider
        self.seed_prompt = seed_prompt
        self.evaluation_dataset = evaluation_dataset
    
    def generate_prompt_variants(self, n: int = 5) -> List[str]:
        """
        Generate n variants of the seed prompt.
        
        Args:
            n: Number of prompt variants to generate
            
        Returns:
            List of prompt variants
        """
        system_prompt = """
        You are a prompt engineering specialist for a large language model.
        Your task is to generate variations of a seed prompt that will improve the model's performance.
        
        Create diverse variations that:
        1. Provide clearer instructions
        2. Add more detailed context
        3. Include examples for few-shot learning
        4. Add constraints to guide the model's responses
        5. Use different phrasings and structures
        
        Generate a JSON array of prompt strings, with no additional text.
        Each prompt should be a complete replacement of the original.
        Make meaningful, substantial changes rather than trivial word substitutions.
        """
        
        user_prompt = f"""
        Generate {n} different variations of this seed prompt:
        
        SEED PROMPT:
        {self.seed_prompt}
        
        Make the variations diverse in their approach and style.
        """
        
        variations_json = self.llm_provider.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )
        
        try:
            return json.loads(variations_json)
        except json.JSONDecodeError:
            # Fallback
            return [self.seed_prompt]
    
    def evaluate_prompt(self, prompt: str) -> float:
        """
        Evaluate a prompt's performance on the evaluation dataset.
        
        Args:
            prompt: The prompt to evaluate
            
        Returns:
            Score between 0 and 1
        """
        total_score = 0.0
        
        for example in self.evaluation_dataset:
            query = example.get("query", "")
            expected = example.get("expected", "")
            
            full_prompt = f"{prompt}\n\nQuery: {query}"
            
            response = self.llm_provider.generate(
                system_prompt="You are a helpful travel planning assistant.",
                user_prompt=full_prompt
            )
            
            # Judge the response quality using another LLM call
            judging_system_prompt = """
            You are a judge evaluating the quality of responses from a travel planning assistant.
            Your task is to score how well the assistant's response matches the expected output.
            
            Score on a scale from 0.0 to 1.0, where:
            - 0.0: Completely off-topic or unhelpful
            - 0.5: Partially relevant but missing key information
            - 1.0: Excellent match with all expected information
            
            Return only the score as a float between 0.0 and 1.0, with no additional text.
            """
            
            judging_user_prompt = f"""
            Assistant's response:
            {response}
            
            Expected information:
            {expected}
            
            Score the response based on how well it addresses the expected information.
            """
            
            score_text = self.llm_provider.generate(
                system_prompt=judging_system_prompt,
                user_prompt=judging_user_prompt
            )
            
            try:
                score = float(score_text.strip())
                total_score += score
            except ValueError:
                # If score parsing fails, use a default score
                total_score += 0.5
        
        # Average score across all examples
        if self.evaluation_dataset:
            return total_score / len(self.evaluation_dataset)
        return 0.0
    
    def optimize_prompt(self, iterations: int = 3, variants_per_iteration: int = 5) -> str:
        """
        Run prompt optimization process to find the best performing prompt.
        
        Args:
            iterations: Number of optimization iterations
            variants_per_iteration: Number of variants to generate per iteration
            
        Returns:
            The best performing prompt
        """
        best_prompt = self.seed_prompt
        best_score = self.evaluate_prompt(best_prompt)
        
        print(f"Initial prompt score: {best_score:.2f}")
        
        for i in range(iterations):
            print(f"Optimization iteration {i+1}/{iterations}...")
            
            # Generate variants based on the current best prompt
            variants = self.generate_prompt_variants(n=variants_per_iteration)
            
            # Evaluate all variants
            for variant in variants:
                score = self.evaluate_prompt(variant)
                print(f"Variant score: {score:.2f}")
                
                if score > best_score:
                    best_score = score
                    best_prompt = variant
                    print(f"New best score: {best_score:.2f}")
        
        print(f"Final best score: {best_score:.2f}")
        return best_prompt