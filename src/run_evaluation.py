#!/usr/bin/env python
"""
Travel Planner Evaluation Pipeline

This script runs the entire evaluation pipeline:
1. Loads test data from the feature extractor data file
2. Runs evaluation on all LLM providers
3. Generates a comprehensive report
4. Provides a summary of results
"""

import os
import logging
import argparse
import json
from dotenv import load_dotenv
import yaml
import pandas as pd
from datetime import datetime

from evaluator import TravelAgentEvaluator
from generate_report import EvaluationReportGenerator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_config(config_path: str):
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def load_test_data(data_path: str, sample_size: int = None):
    """Load test data from JSON file."""
    try:
        with open(data_path, 'r') as f:
            data = json.load(f)
        
        # Extract test cases
        test_cases = []
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and "input_query" in item:
                    test_cases.append({
                        "query": item["input_query"]
                    })
        
        logger.info(f"Loaded {len(test_cases)} test cases from {data_path}")
        
        # Apply sampling if specified
        if sample_size and 0 < sample_size < len(test_cases):
            import random
            random.seed(42)  # For reproducibility
            test_cases = random.sample(test_cases, sample_size)
            logger.info(f"Sampled {len(test_cases)} test cases")
        
        return test_cases
        
    except Exception as e:
        logger.error(f"Error loading test data: {str(e)}")
        return []

def create_run_directory(base_dir: str = "evaluation_runs"):
    """Create a timestamped directory for this evaluation run."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = os.path.join(base_dir, f"run_{timestamp}")
    os.makedirs(run_dir, exist_ok=True)
    logger.info(f"Created run directory: {run_dir}")
    return run_dir

def main():
    """Main entry point for the evaluation pipeline."""
    # Load environment variables
    load_dotenv()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Travel Planner Evaluation Pipeline')
    parser.add_argument('--config', type=str, default='config.yaml', help='Path to config file')
    parser.add_argument('--data', type=str, default='eval-data/feature_extractor_data.json', help='Path to test data file')
    parser.add_argument('--sample-size', type=int, help='Number of test cases to sample')
    parser.add_argument('--output-dir', type=str, default='evaluation_runs', help='Base directory for evaluation outputs')
    parser.add_argument('--skip-evaluation', action='store_true', help='Skip evaluation and use existing results file')
    parser.add_argument('--results-file', type=str, help='Path to existing results file (if skipping evaluation)')
    args = parser.parse_args()
    
    # Create run directory
    run_dir = create_run_directory(args.output_dir)
    
    # Path for evaluation results
    results_file = os.path.join(run_dir, "evaluation_results.json")
    
    # Load configuration
    config = load_config(args.config)
    
    # Run evaluation or use existing results
    if not args.skip_evaluation:
        logger.info("Starting evaluation...")
        
        # Load test data
        test_cases = load_test_data(args.data, args.sample_size)
        
        if not test_cases:
            logger.error("No test cases available. Exiting.")
            return
        
        # Initialize evaluator
        evaluator = TravelAgentEvaluator(config)
        
        # Run evaluation
        evaluator.evaluate_llm_providers(test_cases)
        
        # Save results
        evaluator.generate_report(results_file)
        
        logger.info("Evaluation completed and results saved.")
    else:
        # Use existing results file
        if not args.results_file:
            logger.error("Results file must be specified when skipping evaluation.")
            return
        
        results_file = args.results_file
        logger.info(f"Using existing results file: {results_file}")
    
    # Generate report
    logger.info("Generating evaluation report...")
    
    report_dir = os.path.join(run_dir, "report")
    report_generator = EvaluationReportGenerator(results_file)
    report_generator.generate_full_report(report_dir)
    
    # Generate summary report
    summary_df = report_generator.generate_summary_table()
    summary_file = os.path.join(run_dir, "summary.csv")
    summary_df.to_csv(summary_file, index=False)
    
    # Print summary to console
    logger.info("\n" + "-" * 50)
    logger.info("EVALUATION SUMMARY")
    logger.info("-" * 50)
    
    if not summary_df.empty:
        # Format summary for display
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 120)
        logger.info("\n" + str(summary_df))
        
        # Find best overall provider
        if "overall" in summary_df.columns:
            best_provider = summary_df.loc[summary_df["overall"].idxmax()]["Provider"]
            best_score = summary_df["overall"].max()
            logger.info(f"\nBest performing provider: {best_provider} (Overall score: {best_score:.2f})")
    
    logger.info("\nDetailed report available at:")
    logger.info(f"{os.path.abspath(os.path.join(report_dir, 'index.html'))}")
    logger.info("-" * 50)

if __name__ == "__main__":
    main()