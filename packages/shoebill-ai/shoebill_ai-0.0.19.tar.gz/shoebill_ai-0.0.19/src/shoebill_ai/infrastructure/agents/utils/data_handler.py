import json
import logging

logger = logging.getLogger(__name__)


def parse_json_data(json_string: str) -> dict | None:
    try:
        # Check for empty string
        if not json_string or not json_string.strip():
            logger.warning("Empty JSON string provided")
            return {}

        # First try to extract JSON from Markdown code blocks
        import re
        match = re.search(r'```(?:json)?\s*\n(.*?)\n```', json_string, re.DOTALL)
        if match:
            json_string = match.group(1).strip()
        else:
            # If no code block found, check for various JSON prefixes
            stripped = json_string.strip()
            # Check for <json> prefix
            if stripped.startswith('<json>'):
                json_string = stripped[6:].strip()
            # Check for 'json' prefix
            elif stripped.startswith('json'):
                json_string = stripped[4:].strip()

        # Parse the JSON data
        data = json.loads(json_string)
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON data: {e}")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error while parsing JSON data: {e}")
        return {}
