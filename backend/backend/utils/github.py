import logging
import os
import requests

from enum import Enum


logger = logging.getLogger(__name__)


GITHUB_STATUS_ENABLED = os.getenv("GITHUB_STATUS_ENABLED", False)
if GITHUB_STATUS_ENABLED:
    GITHUB_STATUS_CONTEXT = os.getenv("GITHUB_STATUS_CONTEXT", "EOEPCA Application Quality / Quality Check")
    GITHUB_STATUS_DESCRIPTION = os.getenv("GITHUB_STATUS_DESCRIPTION", "Application quality metrics met all threshold guidelines.")
    GITHUB_STATUS_TARGET_URL = os.getenv("GITHUB_STATUS_TARGET_URL", os.getenv("PUBLIC_URL"))


class GH_CONTEXT_STATUS(str, Enum):
    # Statuses supported by GitHub
    # https://docs.github.com/en/rest/commits/statuses
    PENDING = "pending"
    SUCCESS = "success"
    FAILURE = "failure"
    ERROR = "error"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def has_value(cls, value: str) -> bool:
        return value in cls._value2member_map_

    @classmethod
    def describe(cls, value: str) -> bool:
        if value == GH_CONTEXT_STATUS.PENDING:
            return "Best practices validation is being applied"
        elif value == GH_CONTEXT_STATUS.FAILURE:
            return "Best practices validation failed"
        elif value == GH_CONTEXT_STATUS.SUCCESS:
            return "Best practices validation is successful"
        # Remaining value is ERROR
        return "Failed to apply best practices validation (internal error)"


def post_quality_state(owner, repo, sha, state, statuses_url=None, target_url=None, description=None):
    if not GITHUB_STATUS_ENABLED:
        msg = "GitHub Status is disabled. Not posting status %s to %s/%s"
        logger.warning(msg, state, owner, repo)
        return None
    # Try to get the GitHub owner(organisation)-specific API token, if defined 
    GITHUB_API_TOKEN = os.getenv(f"GITHUB_API_TOKEN__{owner}", None)
    # Otherwise, try to get a global API token
    if not GITHUB_API_TOKEN:
        logger.warning("No specific GitHub API token found for owner %s", owner)
        GITHUB_API_TOKEN = os.getenv(f"GITHUB_API_TOKEN", None)
    if not GITHUB_API_TOKEN:
        logger.error("Missing GitHub API token for posting status to %s/%s", owner, repo)
        return None
    headers = {
        "Authorization": "Bearer " + GITHUB_API_TOKEN,
        "Accept": "application/vnd.github+json",
    }
    if not GH_CONTEXT_STATUS.has_value(state):
        logger.error("Invalid GitHub status: %s", state)
    # If a GitHub API URL is not provided, generate one
    if not statuses_url:
        statuses_url = f"https://api.github.com/repos/{owner}/{repo}/statuses/{sha}"
    if not description:
        description = GH_CONTEXT_STATUS.describe(state)
    payload = {
        "state": state,
        "context": GITHUB_STATUS_CONTEXT,
        "description": description or GITHUB_STATUS_DESCRIPTION,
        "target_url": target_url or GITHUB_STATUS_TARGET_URL,
    }

    response = requests.post(statuses_url, json=payload, headers=headers)
    if response.status_code >= 200 and response.status_code < 300:
        msg = "GitHub status updated for %s/%s: %s = %s"
        logger.info(msg, owner, repo, GITHUB_STATUS_CONTEXT, state)
    elif response.status_code >= 400:
        msg = "Failed to updated GitHub status for %s/%s: %s = %s \n%s"
        err = json.dumps(response.json, indent=2)
        logger.error(msg, owner, repo, GITHUB_STATUS_CONTEXT, state, err)
    return response


def get_properties(event_body):
    # Extract the owner, repository, and commit SHA from the event body
    owner = None
    repo = None
    sha = None
    if "pusher" in event_body:
        owner = event_body.get("repository", {}).get("owner", None).get("login", None)
        repo = event_body.get("repository", {}).get("name", None)
        sha = event_body.get("head_commit", {}).get("id", None)
    elif "pull_request" in event_body:
        # if event_body["action"] => "opened" | "synchronize"
        owner = event_body.get("repository", {}).get("owner", None).get("login", None)
        repo = event_body.get("repository", {}).get("name", None)
        sha = event_body.get("pull_request", {}).get("head", {}).get("sha", {})
    logger.debug("GitHub event properties: owner=%s, repo=%s, sha=%s", owner, repo, sha)
    return owner, repo, sha