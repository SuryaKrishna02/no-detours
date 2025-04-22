import json
import logging
import numpy as np
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt
from typing import Dict, List, Any
from app.agent import TravelPlannerAgent
from api.llm_provider import LLMProvider

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TravelAgentEvaluator:
    """Evaluates multiple LLM providers for the Travel Planning Agent."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Travel Agent Evaluator.
        
        Args:
            config: Configuration dictionary
        """
        logger.info("Initializing TravelAgentEvaluator")
        
        self.config = config
        self.llm_providers = config.get("llm_providers", {})
        self.judge_llm_config = config.get("judge_llm", {})
        self.evaluation_config = config.get("evaluation", {})
        
        # Initialize judge LLM
        self.judge_llm = LLMProvider(
            provider=self.judge_llm_config.get("provider", "anthropic"),
            model=self.judge_llm_config.get("model", "claude-3-7-sonnet"),
            temperature=self.judge_llm_config.get("temperature", 0.2),
            max_tokens=self.judge_llm_config.get("max_tokens", 4000)
        )
        
        # Metrics for evaluation
        self.metrics = self.evaluation_config.get("metrics", [
            "accuracy", "relevance", "completeness", "usefulness", "creativity"
        ])
        
        # Scale for evaluation
        self.scale_min = self.evaluation_config.get("scale_min", 1)
        self.scale_max = self.evaluation_config.get("scale_max", 10)
        
        # Results storage
        self.results = {}
    
    def evaluate_llm_providers(self, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate all LLM providers with the given test cases.
        
        Args:
            test_cases: List of test cases
            
        Returns:
            Evaluation results
        """
        logger.info("Evaluating LLM providers")
        
        results = {}
        
        # For each LLM provider
        for provider_name, provider_config in tqdm(self.llm_providers.items(), desc="Evaluating LLM providers"):
            logger.info(f"Evaluating provider: {provider_name}")
            
            # Clone the config but replace the LLM provider
            provider_specific_config = self.config.copy()
            provider_specific_config["llm"] = provider_config
            
            # Initialize agent with this provider
            agent = TravelPlannerAgent(provider_specific_config)
            
            provider_results = []
            
            # For each test case
            for test_case in tqdm(test_cases, desc=f"Testing {provider_name}", leave=False):
                query = test_case["query"]
                
                try:
                    # Process the query
                    response = agent.process_input(query, eval=True)                    
                    # Get the judge's evaluation
                    evaluation = self.judge_response(query, response, provider_name)
                    
                    # Store the results
                    test_result = {
                        "query": query,
                        "response": response,
                        "evaluation": evaluation
                    }
                    
                    provider_results.append(test_result)
                    
                except Exception as e:
                    logger.error(f"Error evaluating {provider_name} on query '{query}': {str(e)}")
                    provider_results.append({
                        "query": query,
                        "error": str(e)
                    })
            
            results[provider_name] = provider_results
        
        self.results = results
        return results
    
    def judge_response(self, query: str, response: Dict[str, Any], provider_name: str) -> Dict[str, Any]:
        """
        Use the judge LLM to evaluate a response.
        
        Args:
            query: The original user query
            response: The agent's response
            provider_name: Name of the LLM provider
            
        Returns:
            Evaluation metrics
        """
        logger.info(f"Judging response from provider: {provider_name}")
        
        

        # Extract components from the response
        features = json.dumps(response["features"], indent=2)
        queries = json.dumps(response["queries"], indent=2)
        context = json.dumps(response["context"], indent=2)
        output = json.dumps(response["output"], indent=2)

        system_prompt = "You are an expert travel planner evaluator. You are judging the quality of an AI travel planning assistant."
        
        # Construct prompt for the judge
        prompt = f"""
## Original User Query:
"{query}"

## Extracted Features:
{features}

## Generated Search Queries:
{queries}

## Collected Context:
{context}

## Generated Travel Plan:
{output}

Please evaluate the generated travel plan based on Original User Query, Extracted Features,\\
Generated Search Queries, Collected Context using the following metrics, \\
on a scale from {self.scale_min} (worst) to {self.scale_max} (best):
"""
        
        for metric in self.metrics:
            prompt += f"- {metric.capitalize()}: Rate how well the plan performs on {metric}\n"
        
        prompt += """
Provide your ratings as a JSON object with the metrics as keys and ratings as values (integers only).
Then provide a brief explanation for each rating.

Example format:
{{
  "ratings": {{
    "accuracy": 8,
    "relevance": 7,
    ...
  }},
  "explanations": {{
    "accuracy": "The plan accurately addresses...",
    "relevance": "The recommendations are relevant because...",
    ...
  }}
}}
"""
        print("Rating Prompt------------")
        print(prompt)
        
        try:
            # Call the judge LLM
            response = self.judge_llm.generate(
                user_prompt=prompt,
                system_prompt=system_prompt
            )

            print("Came Here-------------------------")
            print(response)
            
            # Extract the JSON from the response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > 0:
                json_str = response[json_start:json_end]
                evaluation = json.loads(json_str)
                
                return evaluation
            else:
                logger.warning(f"Could not extract JSON from judge response: {response}")
                return {"error": "Failed to parse judge response"}
                
        except Exception as e:
            logger.error(f"Error in judge_response: {str(e)}")
            return {"error": str(e)}
    
    def generate_report(self, output_file: str = None) -> Dict[str, Any]:
        """
        Generate a report from the evaluation results.
        
        Args:
            output_file: Path to save the results
            
        Returns:
            Summary of the evaluation results
        """
        logger.info("Generating evaluation report")
        
        if not self.results:
            logger.warning("No results to report")
            return {}
        
        # Calculate average scores for each provider and metric
        summary = {}
        
        for provider, results in self.results.items():
            provider_scores = {metric: [] for metric in self.metrics}
            
            for result in results:
                if "evaluation" in result and "ratings" in result["evaluation"]:
                    ratings = result["evaluation"]["ratings"]
                    
                    for metric in self.metrics:
                        if metric in ratings:
                            provider_scores[metric].append(ratings[metric])
            
            # Calculate averages
            provider_averages = {
                metric: sum(scores) / len(scores) if scores else 0 
                for metric, scores in provider_scores.items()
            }
            
            # Add overall average
            if provider_scores:
                overall = sum(provider_averages.values()) / len(provider_averages)
                provider_averages["overall"] = overall
            
            summary[provider] = provider_averages
        
        # Save results if output file is specified
        if output_file:
            output_path = output_file or self.evaluation_config.get("output_file", "evaluation_results.json")
            
            try:
                with open(output_path, 'w') as f:
                    json.dump({
                        "summary": summary,
                        "detailed_results": self.results
                    }, f, indent=2)
                
                logger.info(f"Results saved to {output_path}")
            except Exception as e:
                logger.error(f"Error saving results: {str(e)}")
        
        return summary
    
    def plot_results(self, summary: Dict[str, Dict[str, float]] = None) -> None:
        """
        Plot the evaluation results.
        
        Args:
            summary: Summary of the evaluation results
        """
        logger.info("Plotting evaluation results")
        
        if not summary and not self.results:
            logger.warning("No results to plot")
            return
        
        if not summary:
            # Generate summary if not provided
            summary = self.generate_report()
        
        # Create dataframe from summary
        data = []
        
        for provider, metrics in summary.items():
            for metric, score in metrics.items():
                data.append({
                    "Provider": provider,
                    "Metric": metric,
                    "Score": score
                })
        
        df = pd.DataFrame(data)
        
        # Plot 1: Overall comparison
        self._plot_overall_comparison(df)
        
        # Plot 2: Metrics comparison across providers
        self._plot_metrics_comparison(df)
        
        # Plot 3: Radar chart per provider
        self._plot_radar_charts(df)
    
    def _plot_overall_comparison(self, df: pd.DataFrame) -> None:
        """Plot overall comparison of providers."""
        plt.figure(figsize=(12, 6))
        
        # Filter for overall metric
        overall_df = df[df["Metric"] == "overall"]
        
        # Sort by score descending
        overall_df = overall_df.sort_values("Score", ascending=False)
        
        # Create bar chart
        bars = plt.bar(overall_df["Provider"], overall_df["Score"])
        
        # Add score labels on top of bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{height:.2f}', ha='center', va='bottom')
        
        plt.xlabel("LLM Provider")
        plt.ylabel("Overall Score")
        plt.title("Overall Performance Comparison of LLM Providers")
        plt.ylim(0, self.scale_max + 0.5)  # Add some space for labels
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # Save plot
        plt.savefig("overall_comparison.png")
        logger.info("Saved overall comparison plot to overall_comparison.png")
    
    def _plot_metrics_comparison(self, df: pd.DataFrame) -> None:
        """Plot metrics comparison across providers."""
        plt.figure(figsize=(15, 8))
        
        # Filter out overall metric
        df_metrics = df[df["Metric"] != "overall"]
        
        # Create grouped bar chart
        providers = df_metrics["Provider"].unique()
        metrics = self.metrics
        
        x = np.arange(len(metrics))
        width = 0.8 / len(providers)
        
        for i, provider in enumerate(providers):
            provider_data = df_metrics[df_metrics["Provider"] == provider]
            scores = [provider_data[provider_data["Metric"] == metric]["Score"].values[0] 
                    if not provider_data[provider_data["Metric"] == metric].empty else 0 
                    for metric in metrics]
            
            offset = i * width - (len(providers) - 1) * width / 2
            plt.bar(x + offset, scores, width, label=provider)
        
        plt.xlabel("Metrics")
        plt.ylabel("Score")
        plt.title("Performance Comparison Across Metrics")
        plt.xticks(x, [m.capitalize() for m in metrics], rotation=45)
        plt.ylim(0, self.scale_max + 0.5)
        plt.legend(title="LLM Provider")
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # Save plot
        plt.savefig("metrics_comparison.png")
        logger.info("Saved metrics comparison plot to metrics_comparison.png")
    
    def _plot_radar_charts(self, df: pd.DataFrame) -> None:
        """Plot radar charts for each provider."""
        # Filter out overall metric
        df_metrics = df[df["Metric"] != "overall"]
        
        # Get unique providers
        providers = df_metrics["Provider"].unique()
        
        # Create subplots - one radar chart per provider
        n_rows = (len(providers) + 1) // 2
        fig, axes = plt.subplots(n_rows, 2, figsize=(15, 5 * n_rows),
                                subplot_kw=dict(polar=True))
        axes = axes.flatten()
        
        # For each provider
        for i, provider in enumerate(providers):
            if i < len(axes):
                ax = axes[i]
                
                # Get provider data
                provider_data = df_metrics[df_metrics["Provider"] == provider]
                
                # Prepare data for radar chart
                metrics = self.metrics
                scores = []
                
                for metric in metrics:
                    metric_score = provider_data[provider_data["Metric"] == metric]["Score"]
                    scores.append(metric_score.values[0] if not metric_score.empty else 0)
                
                # Close the loop
                metrics = [m.capitalize() for m in metrics]
                metrics.append(metrics[0])
                scores.append(scores[0])
                
                # Plot the radar chart
                angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=True)
                ax.plot(angles, scores, 'o-', linewidth=2)
                ax.fill(angles, scores, alpha=0.25)
                ax.set_thetagrids(angles[:-1] * 180 / np.pi, metrics[:-1])
                ax.set_ylim(0, self.scale_max)
                ax.set_title(provider)
                ax.grid(True)
        
        # Remove any unused subplots
        for j in range(i + 1, len(axes)):
            fig.delaxes(axes[j])
        
        plt.tight_layout()
        
        # Save plot
        plt.savefig("radar_charts.png")
        logger.info("Saved radar charts to radar_charts.png")