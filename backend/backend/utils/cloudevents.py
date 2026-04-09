import json
import logging

from cloudevents.conversion import to_structured
from cloudevents.http import CloudEvent
# Used to apply CQL2-JSON filters on the cloudevent content
from pygeofilter.parsers.cql2_json import parse as parse_cql2_json
from pygeofilter.backends.native.evaluate import handle


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


def is_match(filter: dict, payload: dict) -> bool:
    """
    Determine if the dictionnary 'doc' matches the given filter.
    The filter must be encoded using the CQL2-JSON format.
    For example:
    ```python
    filter_json = {
      "op": "and",
      "args": [
        {"op": "=", "args": [{"property": "repository.full_name"}, "SpaceApplications/eoepca-aqbb-test-files"]},
        {"op": "=", "args": [{"property": "ref"}, "refs/heads/main"]}
      ]
    }
    """
    added_files = set()
    deleted_files = set()
    modified_files = set()
    for commit in payload.get("commits", []):
        added_files.update(commit.get("added", []))
        deleted_files.update(commit.get("deleted", []))
        modified_files.update(commit.get("modified", []))
    payload["added_files"] = list(added_files)
    payload["deleted_files"] = list(deleted_files)
    payload["modified_files"] = list(modified_files)
    logger.debug(
        "Files in commit: added=%s, deleted=%s, modified=%s", added_files, deleted_files, modified_files
    )
    # ---
    _is_match = bool(handle(parse_cql2_json(filter), payload))
    logger.debug("Filter matched: %s", _is_match)
    return _is_match
