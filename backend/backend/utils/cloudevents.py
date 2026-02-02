import json
import logging
import os
import time

from cloudevents.conversion import to_structured
from cloudevents.http import CloudEvent


logger = logging.getLogger(__name__)


def decode(body, headers: dict) -> tuple[dict, dict]:
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


def encode(attributes, data, headers=None):
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