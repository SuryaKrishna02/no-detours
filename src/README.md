# Travel Planner Evaluation System

This system evaluates multiple LLM providers for the Travel Planning Agent and generates comprehensive reports on their performance.

## Overview

The evaluation system:

1. Tests multiple LLM providers (OpenAI GPT-3.5/4, Anthropic Claude, Cohere Command, etc.)
2. Evaluates performance on various metrics (accuracy, relevance, completeness, usefulness, creativity)
3. Uses a "judge" LLM to rate responses 
4. Generates detailed reports and visualizations

## Files and Structure

- `config.yaml` - Configuration file for LLM providers and evaluation settings
- `main.py` - Updated main file for running the Travel Planner Agent
- `evaluator.py` - Core evaluation module for testing multiple LLM providers
- `generate_report.py` - Report generation module with visualizations and analysis
- `run_evaluation.py` - Complete evaluation pipeline script

## Requirements

- Python 3.8+
- Required packages: pandas, matplotlib, seaborn, numpy, tqdm, pyyaml, python-dotenv
- API keys for the LLM providers (specified in .env file)

## Installation

1. Set up your Python environment:

```bash
# Create and activate virtual environment (optional)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install pandas matplotlib seaborn numpy tqdm pyyaml python-dotenv
```

2. Create a `.env` file with your API keys:

```
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
COHERE_API_KEY=your_cohere_key
WEATHER_API_KEY=your_weather_api_key
MAPS_API_KEY=your_maps_api_key
```

## Usage

### Running the Complete Evaluation Pipeline

To run the full evaluation pipeline:

```bash
python run_evaluation.py --config config/eval_config.yaml --data eval-data/travel_assistant_data.json --sample-size 10
```

Parameters:
- `--config`: Path to the configuration file (default: config.yaml)
- `--data`: Path to the test data file (default: eval-data/feature_extractor_data.json)
- `--sample-size`: Number of test cases to sample (optional)
- `--output-dir`: Base directory for evaluation outputs (default: evaluation_runs)
- `--skip-evaluation`: Skip evaluation and use existing results file
- `--results-file`: Path to existing results file (if skipping evaluation)

### Generating Reports from Existing Results

If you already have evaluation results and just want to generate reports:

```bash
python run_evaluation.py --skip-evaluation --results-file path/to/evaluation_results.json
```

## Configuration

You can modify the `config.yaml` file to:

1. Add or remove LLM providers
2. Change model parameters (temperature, max tokens)
3. Configure evaluation metrics
4. Set up API providers for weather, maps, and search

Example configuration for an LLM provider:

```yaml
llm_providers:
  openai_gpt4:
    provider: "openai"
    model: "gpt-4"
    temperature: 0.7
    max_tokens: 4000
```

## Evaluation Metrics

The system evaluates travel plans on these metrics (scale 1-10):

- **Accuracy**: How accurately the plan addresses user requirements
- **Relevance**: How relevant the recommendations are to user preferences
- **Completeness**: How comprehensive and detailed the plan is
- **Usefulness**: How practical and helpful the information would be
- **Creativity**: How innovative and personalized the suggestions are

## Reports and Visualizations

The system generates:

1. Summary tables with scores for each provider and metric
2. Heatmaps showing provider performance across metrics
3. Distribution plots for each metric
4. Performance analysis by query category
5. Improvement suggestions
6. Comprehensive HTML report

## Example Workflow

1. Configure LLM providers in `config.yaml`
2. Prepare test data in `eval-data/feature_extractor_data.json`
3. Run the evaluation pipeline: `python run_evaluation.py`
4. Review the generated HTML report in the output directory
5. Analyze the results to determine the best performing LLM provider

## Extending the System

To add support for a new LLM provider:

1. Add the provider configuration to `config.yaml`
2. Ensure the LLMProvider class in `nodetours.api.llm_provider` supports the new provider
3. Add the necessary API key to your `.env` file