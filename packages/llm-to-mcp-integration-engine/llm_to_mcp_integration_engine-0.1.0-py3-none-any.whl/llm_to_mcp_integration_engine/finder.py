import json
from typing import Union, Tuple, Literal

def is_response_json(llm_resp: Union[str, dict]) -> bool:
    """Check if the LLM response is a JSON."""
    if isinstance(llm_resp, dict):
        return True
    try:
        json.loads(llm_resp)
        return True
    except json.JSONDecodeError:
        return False


def find_tools_in_json(response: dict) -> Literal["SELECTED_TOOLS", "SELECTED_TOOL", "NO_TOOLS_SELECTED"]:
    """Find tools in JSON response."""
    if "SELECTED_TOOLS" in response:
        return "SELECTED_TOOLS"
    if "SELECTED_TOOL" in response:
        return "SELECTED_TOOL"
    if "NO_TOOLS_SELECTED" in response:
        return "NO_TOOLS_SELECTED"
    raise ValueError("No tool selection key found")


import re

def find_tools_in_text(text: str) -> Tuple[Literal["SELECTED_TOOLS", "SELECTED_TOOL", "NO_TOOLS_SELECTED"], dict]:
    """Regex-extract JSON fragment."""
    match = re.search(r"\{(.*)\}", text)
    if not match:
        raise ValueError("No JSON fragment found in text")
    json_fragment = match.group(0)
    try:
        response = json.loads(json_fragment)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON fragment")
    return find_tools_in_json(response), response
