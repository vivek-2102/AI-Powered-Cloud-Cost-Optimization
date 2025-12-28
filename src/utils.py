import json
import os
import re
from jsonschema import validate, ValidationError # type: ignore

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "..", "artifacts")
if not os.path.exists(ARTIFACTS_DIR):
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)


def write_json(filepath: str, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def read_json(filepath: str):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def save_description(path,text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Saved project description -> {path}")

def validate_json(data, schema):
    try:
        validate(instance=data, schema=schema)
        return True, None
    except ValidationError as e:
        return False, str(e)
    
def extract_json(text: str):
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"(\[.*\])", text, re.DOTALL)
        if not m:
            raise RuntimeError("Failed to extract billing JSON")
        return json.loads(m.group(1))
