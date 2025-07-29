import re
import json

def extract_json_fragment(text: str) -> dict:
    """Extract JSON fragment from text."""
    match = re.search(r"\{(.*)\}", text)
    if not match:
        return {}
    json_fragment = match.group(0)
    try:
        return json.loads(json_fragment)
    except json.JSONDecodeError:
        return {}


# then reuse json_handler routines
