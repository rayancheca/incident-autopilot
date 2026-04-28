import json
import re


def extract_json_block(text: str) -> str | None:
    """Extract the first JSON object or array from a text blob, tolerating surrounding noise."""
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```", text, re.DOTALL)
    if fence_match:
        return fence_match.group(1)

    brace_match = re.search(r"(\{.*\})", text, re.DOTALL)
    if brace_match:
        return brace_match.group(1)

    return None


def parse_json_with_repair(text: str) -> dict | None:
    """Attempt to parse JSON; on failure, try extracting and re-parsing."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    extracted = extract_json_block(text)
    if not extracted:
        return None

    try:
        result = json.loads(extracted)
        if isinstance(result, dict):
            return result
        return None
    except json.JSONDecodeError:
        return None
