import os
import json
from .llm_client_call import LLMClient
from .utils import write_json, validate_json, read_json, extract_json
import random


SCHEMA_PATH = os.path.join(
    os.path.dirname(__file__), "schemas", "recommendations_schema.json"
)

SYSTEM_PROMPT = (
    "You are a JSON-only assistant. " "Return ONLY valid JSON. No explanations."
)

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

ITEM_PROMPT_TEMPLATE = """
Generate ONE cloud cost optimization recommendation
specifically for the service: "{service}".

Rules:
- Return ONLY valid JSON
- Follow the schema exactly
- Do NOT repeat services
- Do NOT include explanations or extra text

Schema:
{schema}

Project Profile:
{profile}

Synthetic Billing
{billing}

You have to mandatorily check the billing for the given service and
generate a recommendation that can help optimize costs for the given service.

Your current cost here means cost after implementing the recommendation.And potential savings means cost after subtracting the cost from syntethic billing and current recommendation cost.

I want you to take time and read the documentation of azure and gcp cost management and billing to understand how costs are generated for different services.

"""


def compute_total_cost(billing):
    if isinstance(billing, list):
        total = 0.0
        for item in billing:
            if isinstance(item, dict):
                cost = item.get("cost_inr") or item.get("cost")
                if isinstance(cost, (int, float)):
                    total += float(cost)
        return total

    return 0.0


def generate_recommendations(
    profile: dict, llm: LLMClient, billing: list[dict], save_path: str | None = None
):
    schema = read_json(SCHEMA_PATH)

    min_items = schema["properties"]["recommendations"].get("minItems", 6)
    max_items = schema["properties"]["recommendations"].get("maxItems", 10)
    target_count = random.randint(min_items, max_items)

    item_schema = schema["properties"]["recommendations"]["items"]

    recommendations = []

    budget = profile.get("budget_inr_per_month", 0)
    total_cost = compute_total_cost(billing)
    variance = total_cost - budget
    over_budget = total_cost > budget

    for service in SERVICE_POOL:
        if len(recommendations) >= target_count:
            break

        prompt = ITEM_PROMPT_TEMPLATE.format(
            service=service,
            schema=json.dumps(item_schema, indent=2),
            profile=json.dumps(profile, indent=2),
            billing=json.dumps(billing, indent=2),
        )

        response_text = llm.call(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=prompt,
        )

        parsed = extract_json(response_text)
        if not isinstance(parsed, dict):
            continue

        valid, err = validate_json(parsed, item_schema)
        if not valid:
            continue

        recommendations.append(parsed)

    final = {
        "total_cost_inr": total_cost,
        "budget_inr": budget,
        "variance_inr": variance,
        "over_budget": over_budget,
        "recommendations": recommendations[:max_items],
    }

    valid, err = validate_json(final, schema)
    if not valid:
        raise ValueError(
            f"Generated recommendations JSON failed schema validation: {err}"
        )

    if save_path:
        write_json(save_path, final)

    return final
