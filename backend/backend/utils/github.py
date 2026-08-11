import functools
import json
import logging
import os
import re
import requests

from enum import Enum
from backend.utils.tools import getenv_bool
from urllib.parse import urlparse


logger = logging.getLogger(__name__)


GITHUB_STATUS_ENABLED = getenv_bool("GITHUB_STATUS_ENABLED", False)
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
    def map_value(cls, value: str) -> str:
        value = value.lower()
        if value.startswith("succ") or value.startswith("pass") or value in ["ok", "yes"]:
            return GH_CONTEXT_STATUS.SUCCESS
        if value.startswith("fail") or value in ["nok", "ko", "no"]:
            return GH_CONTEXT_STATUS.FAILURE
        if value.startswith("wait") or value in ["pending"]:
            return GH_CONTEXT_STATUS.PENDING
        if value.startswith("err"):
            return GH_CONTEXT_STATUS.ERROR
        return None

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


def require_github_status_enabled(func):
    """
    Decorator that skips the wrapped function (returning None) unless
    the global GITHUB_STATUS_ENABLED flag is True.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not GITHUB_STATUS_ENABLED:
            return None
        return func(*args, **kwargs)
    return wrapper


def request_headers(owner, token=None):
    if token:
        return {
            "Authorization": "Bearer " + token,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
    # Try to get the GitHub owner(organisation)-specific API token, if defined
    api_token = os.getenv(f"GITHUB_API_TOKEN__{owner}", None)
    # Otherwise, try to get a global API token
    if not api_token:
        logger.warning("No specific GitHub API token found for owner %s", owner)
        api_token = os.getenv(f"GITHUB_API_TOKEN", None)
    if not api_token:
        logger.error("Missing GitHub API token for posting status to %s/%s", owner, repo)
        return None
    return {
        "Authorization": "Bearer " + api_token,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


@require_github_status_enabled
def post_quality_state(owner, repo, sha, state, statuses_url=None, target_url=None, description=None):
    headers = request_headers(owner)
    if not headers:
        return None
    state = GH_CONTEXT_STATUS.map_value(state)
    if not GH_CONTEXT_STATUS.has_value(state):
        logger.error("Invalid GitHub status: %s", state)
    # If a short SHA is provided, retrieve the full one from GitHub
    if len(sha) < 40:
        sha = get_commit_sha(owner, repo, sha)
        if isinstance(sha, requests.Response):
            logger.error("Failed to obtain full commit SHA value: %s", sha)
            return sha
        logger.info("Obtained full commit SHA value: %s", sha)
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
    # Submit the status change request
    response = requests.post(statuses_url, json=payload, headers=headers)
    if response.status_code >= 200 and response.status_code < 300:
        msg = "GitHub status updated for %s/%s: %s = %s"
        logger.info(msg, owner, repo, GITHUB_STATUS_CONTEXT, state)
    elif response.status_code >= 400:
        msg = "Failed to update GitHub status for %s/%s: %s = %s\n%s"
        try:
            err = json.dumps(response.json(), indent=2)
            logger.error(msg, owner, repo, GITHUB_STATUS_CONTEXT, state, err)
        except Exception as e:
            logger.error(e)
            logger.error(msg, owner, repo, GITHUB_STATUS_CONTEXT, state, response.text)
    return response


@require_github_status_enabled
def post_pr_quality_state(owner, repo, pr_id, state, statuses_url=None, target_url=None, description=None):
    sha = get_pr_head_sha(owner, repo, pr_id)
    if isinstance(sha, requests.Response):
        logger.error("Failed to obtain head commit SHA from PR %s: %s", pr_id, sha)
        return sha
    logger.info("Obtained head commit SHA from PR %s: %s", pr_id, sha)
    return post_quality_state(owner, repo, sha, state, statuses_url, target_url, description)


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


def parse_repo_url(url):
    """
    Extract (owner, repo) from a GitHub repository URL.

    Supports:
      - https://github.com/owner/repo
      - https://github.com/owner/repo/
      - https://github.com/owner/repo.git
      - https://github.com/owner/repo/pull/123
      - https://github.com/owner/repo/tree/main
      - git@github.com:owner/repo.git
      - github.com/owner/repo (no scheme)

    Returns:
        tuple[str, str]: (owner, repo)

    Raises:
        ValueError: if the URL doesn't match a recognizable GitHub repo format.
    """
    if not url:
        raise ValueError("URL is empty")

    url = url.strip()

    # SSH-style: git@github.com:owner/repo.git
    ssh_match = re.match(r"^git@github\.com:([^/]+)/([^/]+?)(\.git)?/?$", url)
    if ssh_match:
        return ssh_match.group(1), ssh_match.group(2)

    # Add a scheme if missing, so urlparse handles it consistently
    if not re.match(r"^https?://", url):
        url = "https://" + url

    parsed = urlparse(url)

    if "github.com" not in parsed.netloc:
        raise ValueError(f"Not a GitHub URL: {url}")

    # path looks like: /owner/repo or /owner/repo/pull/123 etc.
    parts = [p for p in parsed.path.split("/") if p]

    if len(parts) < 2:
        raise ValueError(f"Could not extract owner/repo from URL: {url}")

    owner, repo = parts[0], parts[1]
    repo = re.sub(r"\.git$", "", repo)  # strip trailing .git if present

    return owner, repo


@require_github_status_enabled
def get_commit_sha(owner, repo, short_sha, token=None):
    """
    Resolve a short commit SHA to its full 40-character SHA using the GitHub API.

    Args:
        owner (str): Repository owner (user or org).
        repo (str): Repository name.
        short_sha (str): Abbreviated commit SHA (e.g. 7+ hex chars).
        token (str, optional): GitHub personal access token, for auth
            (recommended to avoid low rate limits on unauthenticated requests).

    Returns:
        str: The full 40-character commit SHA.

    Raises:
        requests.HTTPError: if the request fails (e.g. 404 not found, 422 ambiguous SHA).
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/commits/{short_sha}"
    headers = request_headers(owner, token)
    response = requests.get(url, headers=headers)
    if response.status_code >= 400:
        return response
    return response.json()["sha"]


@require_github_status_enabled
def get_pr_head_sha(owner, repo, pr_number, token=None):
    """
    Retrieve the SHA of the head commit of a GitHub pull request.

    Args:
        owner (str): Repository owner (user or org).
        repo (str): Repository name.
        pr_number (int or str): Pull request number.
        token (str, optional): GitHub personal access token, for auth
            (recommended to avoid low rate limits on unauthenticated requests).

    Returns:
        str: The full 40-character SHA of the PR's head commit.

    Raises:
        requests.HTTPError: if the request fails (e.g. 404 if the PR doesn't exist).
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    headers = request_headers(owner, token)
    response = requests.get(url, headers=headers)
    if response.status_code >= 400:
        return response
    return response.json()["head"]["sha"]