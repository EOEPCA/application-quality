import json
import logging

from cloudevents.conversion import to_structured
from cloudevents.http import CloudEvent


logger = logging.getLogger(__name__)


def decode(body: str, headers: dict) -> tuple[dict, dict]:
    """
    Decode CloudEvent and return the payload and the headers
    """
    headers_dict = {}
    payload_dict = {}
    try:
        # Extract the event headers
        for key, value in headers:
            if key.startswith('HTTP_'):
                # Convert 'HTTP_X_FORWARDED_FOR' to 'X-Forwarded-For'
                header_name = key[5:].replace('_', '-').title()
                headers_dict[header_name] = value
            elif key in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                # Add special headers not prefixed with HTTP_
                headers_dict[key.replace('_', '-').title()] = value

        # Extract the event data
        if body:
            payload_dict = json.loads(body.decode('utf-8'))
        else:
            payload_dict = {}

        logger.debug("Event Headers:\n%s", json.dumps(headers_dict, indent=2))
        logger.debug("Event Data:\n%s", json.dumps(payload_dict, indent=2))

    except json.JSONDecodeError:
        logger.error("JSONDecodeError")
        return Response(
            {"error": "Invalid JSON payload in event body"},
            status=status.HTTP_400_BAD_REQUEST
        )

    return payload_dict, headers_dict


def encode(attributes: dict, data: dict):
    event = CloudEvent(attributes, data)
    logger.debug("Event: %s", event)
    _ignore, payload = to_structured(event)
    headers_dict = {
        f"Ce-{k}": v 
        for k, v in attributes.items()
    }
    logger.debug("Headers: %s", headers_dict)
    logger.debug("Payload: %s", payload)
    return payload, headers_dict


def is_match(filter_node: dict, payload: dict) -> bool:
    """
    Evaluates a CQL2-JSON filter against a Python dictionary.
    Supports 'and', 'or', and '=' operators with nested property access.
    Example filter:
    ```json
    {
      "op": "and",
      "args": [
        {"op": "=", "args": [{"property": "repository.full_name"}, "SpaceApplications/eoepca-aqbb-test-files"]},
        {"op": "=", "args": [{"property": "ref"}, "refs/heads/main"]}
      ]
    }
    ```
    """
    logger.debug("Filter node: %s", filter_node)
    op = filter_node.get("op", "").lower()
    args = filter_node.get("args", [])
    # Handle Logical Operators
    if op == "and":
        return all(is_match(arg, payload) for arg in args)
    if op == "or":
        return any(is_match(arg, payload) for arg in args)
    # Handle Comparison Operators
    if op == "=":
        left_raw = args[0]
        right = args[1] # The constant value
        # Resolve the property value (e.g., "repository.full_name")
        left_val = None
        if isinstance(left_raw, dict) and "property" in left_raw:
            path = left_raw["property"].split('.')
            left_val = payload
            for part in path:
                if isinstance(left_val, dict):
                    left_val = left_val.get(part)
                else:
                    left_val = None
                    break
        else:
            left_val = left_raw

        return left_val == right
    # Default to False for unknown operators
    return False