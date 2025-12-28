import os
import json
import re
from .llm_client_call import LLMClient
from .utils import write_json, validate_json, read_json, extract_json

SCHEMA_PATH = os.path.join(
    os.path.dirname(__file__), "schemas", "project_profile_schema.json"
)


PROMPT_TEMPLATE = """
Follow the JSON schema exactly.

Rules:
- If the project name is not explicitly given, infer a concise project_name from the description.
- project_name MUST be a short title (e.g. "Food Delivery App").
- Return ONLY valid JSON. No explanations.

Schema:
{schema}

Project Description:
{description}
"""


def generate_project_profile(
    description_text: str, llm: LLMClient, save_path: str = None
):
    schema = read_json(SCHEMA_PATH)
    prompt = PROMPT_TEMPLATE.format(
        schema=json.dumps(schema, indent=2), description=description_text
    )
    response_text = llm.call(
        system_prompt="You are a JSON-only assistant. Return only valid JSON.",
        user_prompt=prompt,
    )
    parsed = extract_json(response_text)

    valid, err = validate_json(parsed, schema)
    if not valid:
        raise ValueError(
            f"Generated project_profile JSON failed schema validation: {err}"
        )
    if save_path:
        write_json(save_path, parsed)
    return parsed
