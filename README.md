# AI-Powered Cloud Cost Optimizer

This is a small Python project that uses an LLM to generate cloud cost optimization recommendations based on a project description and billing data. It runs locally and produces structured JSON and HTML reports.

## What it does

Takes a project description

Generates a structured project profile

Uses billing data (synthetic or real) to calculate costs

Generates cloud cost optimization recommendations

Exports a final report as JSON or HTML

All outputs follow JSON schemas so they are consistent and predictable.

## Requirements

Python 3.10+

Hugging Face API key (for LLM calls)

## Setup

Install dependencies:

pip install -r requirements.txt

## Configuration

Create a .env file in the project root:

HF_API_KEY=your_huggingface_api_key
HF_MODEL_ID=meta-llama/Meta-Llama-3-8B-Instruct

## Running the project

Run the CLI as a module:

python -m src.cli


## The CLI will guide you through:

Entering a project description

Generating a project profile

Providing or generating billing data

Generating recommendations

Exporting the final report

## Output

Generated files are written to the artifacts/ directory.

## Common outputs:

project_profile.json

mock_billing.json

recommendations.json

cost_optimization_report.json

## Schemas used for validation are in:

src/schemas/

## Notes

All cost calculations (totals, variance, budget checks) are done in Python, not by the LLM.

The LLM is only used to generate structured data and explanations.

Real cloud billing data (Azure / GCP) can be plugged in later without changing the recommendation logic.

