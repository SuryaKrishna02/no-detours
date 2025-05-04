"""
generate_report.py

Evaluation report generator module for travel planner LLM evaluation system.
Creates comprehensive performance reports with visualizations to compare different LLM providers.
"""

import os
import json
import logging
import argparse
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from typing import Dict, List, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EvaluationReportGenerator:
    """
    Generates detailed reports and visualizations from evaluation results.
    
    This class processes evaluation results from multiple LLM providers,
    creates performance visualizations, and generates comprehensive HTML reports
    with metric analysis and improvement suggestions.
    """
    
    def __init__(self, results_file: str):
        """
        Initialize the report generator.
        
        Args:
            results_file: Path to the JSON file containing evaluation results
        """
        self.results_file = results_file
        self.results = self._load_results()
        
        # Extract summary and detailed results
        self.summary = self.results.get("summary", {})
        self.detailed_results = self.results.get("detailed_results", {})
        
        # Extract metrics from the first provider's summary
        if self.summary:
            first_provider = next(iter(self.summary.values()))
            self.metrics = [m for m in first_provider.keys() if m != "overall"]
        else:
            self.metrics = []
    
    def _load_results(self) -> Dict[str, Any]:
        """
        Load evaluation results from the JSON file.
        
        Returns:
            Dictionary containing the evaluation results with summary and detailed data.
            Returns empty dict if file cannot be loaded.
        """
        try:
            with open(self.results_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading results: {str(e)}")
            return {}
    
    def generate_summary_table(self) -> pd.DataFrame:
        """
        Generate a summary table of the evaluation results.
        
        Creates a DataFrame containing scores for each provider across all metrics,
        with 'overall' metric moved to the end of the columns for better readability.
        
        Returns:
            DataFrame with provider names and their scores for each metric.
            Returns empty DataFrame if no summary data is available.
        """
        if not self.summary:
            return pd.DataFrame()
        
        # Create a list of dictionaries for the table
        rows = []
        
        for provider, metrics in self.summary.items():
            row = {"Provider": provider}
            row.update(metrics)
            rows.append(row)
        
        # Create DataFrame
        df = pd.DataFrame(rows)
        
        # Reorder columns to put 'overall' at the end
        cols = ["Provider"] + [c for c in df.columns if c != "Provider" and c != "overall"]
        if "overall" in df.columns:
            cols.append("overall")
        
        df = df[cols]
        
        return df
    
    def generate_heatmap(self, output_file: str = "heatmap.png") -> None:
        """
        Generate a heatmap visualization of provider performance across metrics.
        
        Creates a color-coded heatmap showing how each provider performs on each metric,
        allowing for quick visual comparison of strengths and weaknesses.
        
        Args:
            output_file: Path where the heatmap image will be saved
        """
        if not self.summary:
            logger.warning("No summary data available for heatmap")
            return
        
        # Prepare data
        data = []
        
        for provider, metrics in self.summary.items():
            for metric, score in metrics.items():
                if metric != "overall":  # Exclude overall from heatmap
                    data.append({
                        "Provider": provider,
                        "Metric": metric.capitalize(),
                        "Score": score
                    })
        
        df = pd.DataFrame(data)
        
        # Create pivot table
        pivot = df.pivot(index="Provider", columns="Metric", values="Score")
        
        # Create heatmap
        plt.figure(figsize=(12, 8))
        sns.heatmap(pivot, annot=True, cmap="YlGnBu", fmt=".2f", linewidths=.5)
        plt.title("LLM Provider Performance Across Metrics")
        plt.tight_layout()
        
        # Save heatmap
        plt.savefig(output_file)
        logger.info(f"Saved heatmap to {output_file}")
    
    def generate_metric_distribution(self, output_dir: str = "metric_plots") -> None:
        """
        Generate distribution plots for each metric across all providers.
        
        Creates violin plots showing the distribution of scores for each metric,
        revealing the variance and central tendency of provider performance.
        
        Args:
            output_dir: Directory where the distribution plots will be saved
        """
        if not self.detailed_results:
            logger.warning("No detailed results available for distribution plots")
            return
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # For each metric
        for metric in self.metrics:
            # Collect scores for this metric from all providers and test cases
            scores_by_provider = {}
            
            for provider, results in self.detailed_results.items():
                scores = []
                
                for result in results:
                    if "evaluation" in result and "ratings" in result["evaluation"]:
                        rating = result["evaluation"]["ratings"].get(metric)
                        if rating is not None:
                            scores.append(rating)
                
                if scores:
                    scores_by_provider[provider] = scores
            
            if not scores_by_provider:
                continue
            
            # Create violin plot
            plt.figure(figsize=(12, 6))
            
            data = []
            labels = []
            
            for provider, scores in scores_by_provider.items():
                data.append(scores)
                labels.append(provider)
            
            plt.violinplot(data, showmeans=True, showmedians=True)
            plt.xticks(range(1, len(labels) + 1), labels, rotation=45)
            plt.ylabel("Score")
            plt.title(f"Distribution of {metric.capitalize()} Scores Across Providers")
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            plt.tight_layout()
            
            # Save plot
            output_file = os.path.join(output_dir, f"{metric}_distribution.png")
            plt.savefig(output_file)
            logger.info(f"Saved {metric} distribution plot to {output_file}")
    
    def generate_performance_by_query(self, output_file: str = "query_performance.png") -> None:
        """
        Generate a plot showing performance by query category.
        
        Creates a grouped bar chart comparing how providers perform across different
        types of travel queries (Cultural, Beach/Water, Food, Nature/Outdoors, General).
        
        Args:
            output_file: Path where the query performance plot will be saved
        """
        if not self.detailed_results:
            logger.warning("No detailed results available for query performance plot")
            return
        
        # Extract query features to categorize them
        query_categories = {}
        
        for provider, results in self.detailed_results.items():
            for result in results:
                query = result.get("query", "")
                
                # Simple categorization based on keywords in the query
                category = "General"
                
                if "museum" in query.lower() or "historical" in query.lower():
                    category = "Cultural"
                elif "beach" in query.lower() or "snorkel" in query.lower() or "water" in query.lower():
                    category = "Beach/Water"
                elif "food" in query.lower() or "cuisine" in query.lower() or "restaurant" in query.lower():
                    category = "Food"
                elif "hiking" in query.lower() or "mountain" in query.lower() or "nature" in query.lower():
                    category = "Nature/Outdoors"
                
                # Store the category
                if query not in query_categories:
                    query_categories[query] = category
        
        # Collect overall scores by provider and category
        category_scores = {}
        
        for provider, results in self.detailed_results.items():
            for result in results:
                query = result.get("query", "")
                category = query_categories.get(query, "General")
                
                if "evaluation" in result and "ratings" in result["evaluation"]:
                    # Calculate average score across all metrics
                    ratings = result["evaluation"]["ratings"]
                    avg_score = sum(ratings.values()) / len(ratings) if ratings else 0
                    
                    if category not in category_scores:
                        category_scores[category] = {}
                    
                    if provider not in category_scores[category]:
                        category_scores[category][provider] = []
                    
                    category_scores[category][provider].append(avg_score)
        
        # Calculate average scores by category and provider
        avg_category_scores = {}
        
        for category, providers in category_scores.items():
            avg_category_scores[category] = {}
            
            for provider, scores in providers.items():
                avg_category_scores[category][provider] = sum(scores) / len(scores) if scores else 0
        
        # Create grouped bar chart
        plt.figure(figsize=(14, 8))
        
        # Get all categories and providers
        categories = list(avg_category_scores.keys())
        providers = list(self.detailed_results.keys())
        
        # Set width of bars
        width = 0.8 / len(providers)
        x = np.arange(len(categories))
        
        # Plot bars for each provider
        for i, provider in enumerate(providers):
            scores = []
            
            for category in categories:
                score = avg_category_scores.get(category, {}).get(provider, 0)
                scores.append(score)
            
            offset = i * width - (len(providers) - 1) * width / 2
            plt.bar(x + offset, scores, width, label=provider)
        
        plt.xlabel("Query Category")
        plt.ylabel("Average Score")
        plt.title("Performance by Query Category")
        plt.xticks(x, categories)
        plt.legend(title="LLM Provider")
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # Save plot
        plt.savefig(output_file)
        logger.info(f"Saved query performance plot to {output_file}")
    
    def generate_improvement_suggestions(self) -> Dict[str, List[str]]:
        """
        Generate improvement suggestions for each provider based on their weakest metrics.
        
        Analyzes provider performance to identify the 2 lowest-scoring metrics for each provider,
        then generates specific suggestions for improvement in those areas.
        
        Returns:
            Dictionary mapping provider names to lists of improvement suggestions.
            Returns empty dict if no summary data is available.
        """
        if not self.summary:
            logger.warning("No summary data available for improvement suggestions")
            return {}
        
        suggestions = {}
        
        for provider, metrics in self.summary.items():
            # Find the weakest metrics (excluding overall)
            metric_scores = {m: s for m, s in metrics.items() if m != "overall"}
            sorted_metrics = sorted(metric_scores.items(), key=lambda x: x[1])
            
            # Get the 2 weakest metrics
            weak_metrics = sorted_metrics[:2] if len(sorted_metrics) >= 2 else sorted_metrics
            
            # Generate suggestions
            provider_suggestions = []
            
            for metric, _ in weak_metrics:
                if metric == "accuracy":
                    provider_suggestions.append(
                        "Improve accuracy by enhancing feature extraction and ensuring all user preferences are captured correctly."
                    )
                elif metric == "relevance":
                    provider_suggestions.append(
                        "Enhance relevance by better matching recommendations to user preferences and ensuring search queries target specific user interests."
                    )
                elif metric == "completeness":
                    provider_suggestions.append(
                        "Make itineraries more complete by adding more details about attractions, timing, transportation between sites, and practical information."
                    )
                elif metric == "usefulness":
                    provider_suggestions.append(
                        "Increase usefulness by adding local tips, off-the-beaten-path suggestions, and practical information about opening hours, tickets, and costs."
                    )
                elif metric == "creativity":
                    provider_suggestions.append(
                        "Boost creativity by offering unique experiences, personalized recommendations, and themed itinerary options that go beyond standard tourist attractions."
                    )
            
            suggestions[provider] = provider_suggestions
        
        return suggestions
    
    def generate_html_report(self, output_file: str = "evaluation_report.html") -> None:
        """
        Generate a comprehensive HTML report of the evaluation results.
        
        Creates an HTML page that includes the summary table, heatmap,
        performance by query category plot, metric distribution plots,
        and improvement suggestions for each provider.
        
        Args:
            output_file: Path where the HTML report will be saved
        """
        # Generate all the components
        summary_df = self.generate_summary_table()
        self.generate_heatmap("heatmap.png")
        self.generate_metric_distribution("metric_plots")
        self.generate_performance_by_query("query_performance.png")
        suggestions = self.generate_improvement_suggestions()
        
        # Create HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Travel Planner LLM Evaluation Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #2c3e50; }}
                h2 {{ color: #3498db; margin-top: 30px; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
                th {{ background-color: #3498db; color: white; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
                .metric-plots {{ display: flex; flex-wrap: wrap; justify-content: center; }}
                .metric-plot {{ margin: 10px; }}
                .suggestions {{ margin: 20px 0; }}
                .provider-suggestion {{ margin: 10px 0; padding: 10px; background-color: #f8f9fa; border-left: 4px solid #3498db; }}
            </style>
        </head>
        <body>
            <h1>Travel Planner LLM Evaluation Report</h1>
            
            <h2>Overall Performance Summary</h2>
            <table>
                <tr>
                    {"".join([f"<th>{col}</th>" for col in summary_df.columns])}
                </tr>
                {"".join([
                    f"<tr>{''.join([f'<td>{row[col]:.2f}</td>' if isinstance(row[col], float) else f'<td>{row[col]}</td>' for col in summary_df.columns])}</tr>"
                    for _, row in summary_df.iterrows()
                ])}
            </table>
            
            <h2>Performance Heatmap</h2>
            <div style="text-align: center;">
                <img src="heatmap.png" alt="Performance Heatmap" style="max-width: 100%;">
            </div>
            
            <h2>Performance by Query Category</h2>
            <div style="text-align: center;">
                <img src="query_performance.png" alt="Performance by Query Category" style="max-width: 100%;">
            </div>
            
            <h2>Metric Distribution</h2>
            <div class="metric-plots">
                {"".join([
                    f'<div class="metric-plot"><img src="metric_plots/{metric}_distribution.png" alt="{metric} Distribution" style="width: 450px;"></div>'
                    for metric in self.metrics
                ])}
            </div>
            
            <h2>Improvement Suggestions</h2>
            <div class="suggestions">
                {"".join([
                    f'<div class="provider-suggestion"><h3>{provider}</h3><ul>{"".join([f"<li>{suggestion}</li>" for suggestion in provider_suggs])}</ul></div>'
                    for provider, provider_suggs in suggestions.items()
                ])}
            </div>
        </body>
        </html>
        """
        
        # Write HTML to file
        with open(output_file, 'w') as f:
            f.write(html_content)
        
        logger.info(f"Saved HTML report to {output_file}")
    
    def generate_full_report(self, output_dir: str = "evaluation_report") -> None:
        """
        Generate a full report with all components.
        
        Creates a directory structure containing all visualization files and 
        the HTML report, ensuring proper paths for all referenced assets.
        
        Args:
            output_dir: Directory where the report and all assets will be saved
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, "metric_plots"), exist_ok=True)
        
        # Generate components with paths in the output directory
        heatmap_path = os.path.join(output_dir, "heatmap.png")
        metric_plots_dir = os.path.join(output_dir, "metric_plots")
        query_performance_path = os.path.join(output_dir, "query_performance.png")
        html_report_path = os.path.join(output_dir, "index.html")
        
        # Generate all plots and reports
        self.generate_heatmap(heatmap_path)
        self.generate_metric_distribution(metric_plots_dir)
        self.generate_performance_by_query(query_performance_path)
        self.generate_html_report(html_report_path)
        
        logger.info(f"Generated full evaluation report in {output_dir}")


def main():
    """
    Main entry point for the report generator.
    
    Parses command line arguments, initializes the report generator,
    and generates the full evaluation report.
    """
    parser = argparse.ArgumentParser(description='Travel Planner Evaluation Report Generator')
    parser.add_argument('--results', type=str, required=True, help='Path to evaluation results JSON file')
    parser.add_argument('--output-dir', type=str, default='evaluation_report', help='Directory to save the report')
    args = parser.parse_args()
    
    # Initialize report generator
    report_generator = EvaluationReportGenerator(args.results)
    
    # Generate full report
    report_generator.generate_full_report(args.output_dir)


if __name__ == "__main__":
    main()