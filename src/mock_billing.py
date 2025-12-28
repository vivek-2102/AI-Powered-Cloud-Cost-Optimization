import json
import re
import os
from .llm_client_call import LLMClient
from .utils import validate_json, write_json, read_json, extract_json

SCHEMA_PATH = os.path.join(
    os.path.dirname(__file__), "schemas", "synthetic_billing_schema.json"
)


def generate_synthetic_billing(profile: dict, llm: LLMClient, save_path: str = None):
    schema = read_json(SCHEMA_PATH)

    system_prompt = (
        "You are a cloud cost modeling assistant. "
        "Return ONLY valid JSON. No explanations."
    )

    USER_PROMPT_TEMPLATE = """
Generate a synthetic monthly cloud billing breakdown.

Rules:
- Output MUST strictly follow the JSON schema below
- Output MUST be a JSON array
- Each item must include: service, cost_inr, desc
- Costs must be realistic
- Total cost should be close to budget {budget} INR it can be slightly below or above but not exceed by more than 20%

Schema:
{schema}

Project Profile:
{profile}

SERVICE_POOL = [
    "Compute",
    "Database",
    "Storage",
    "Networking",
    "Monitoring",
    "Containers",
    "Security",
    "Analytics",
]
You have to generate costs for all  the services in the SERVICE_POOL.
I want you to take time and read the documentation of azure and gcp cost management and billing to understand how costs are generated for different services.
Generate the synthetic billing JSON now.
"""

    user_prompt = USER_PROMPT_TEMPLATE.format(
        schema=json.dumps(schema, indent=2),
        profile=json.dumps(profile, indent=2),
        budget=profile.get("budget_inr_per_month"),
    )

    # call LLM
    response_text = llm.call(system_prompt=system_prompt, user_prompt=user_prompt)

    # extract and validate JSON
    parsed = extract_json(response_text)

    valid, err = validate_json(parsed, schema)
    if not valid:
        raise ValueError(f"Synthetic billing schema validation failed: {err}")

    if save_path:
        write_json(save_path, parsed)

    return parsed
