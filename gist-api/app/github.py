"""
GitHub API client.

Responsible for fetching and shaping public gist data.
Kept separate from main.py so it can be mocked independently in tests.
"""

import time # Used for implementing a simple in-memory TTL cache to reduce GitHub API calls.
import httpx # Used for making asynchronous HTTP requests to the GitHub API.
from typing import Optional # Used for type hinting the return value of get_user_gists (list of gists or None if user not found).

# Constants and simple in-memory cache for GitHub API responses.
GITHUB_API_BASE = "https://api.github.com" # Base URL for GitHub API requests.
GITHUB_HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
} # GitHub API versioning header to ensure consistent responses.

# Simple in-memory TTL (Time-To-Live) cache to stay within GitHub's 60 req/hour
# unauthenticated rate limit on repeated calls for the same user.
_cache: dict = {}
CACHE_TTL_SECONDS = 60


def _cache_key(username: str, page: int, per_page: int) -> tuple:
    return (username.lower(), page, per_page)


def _get_cached(key: tuple) -> Optional[list]:
    entry = _cache.get(key)
    if entry and time.time() < entry["expires"]:
        return entry["data"]
    return None


def _set_cache(key: tuple, data: list) -> None:
    _cache[key] = {"data": data, "expires": time.time() + CACHE_TTL_SECONDS} # Store the API response in the cache with an expiration time to avoid stale data and manage memory usage.


async def get_user_gists(
    username: str,
    page: int = 1,
    per_page: int = 30,
) -> Optional[list]:
    """
    Fetch public gists for a GitHub user.

    Returns a list of raw gist objects, or None if the user does not exist.
    Raises httpx.HTTPStatusError / httpx.RequestError on unexpected failures.
    """
    key = _cache_key(username, page, per_page)
    cached = _get_cached(key) # Check cache before making an API call to avoid unnecessary requests and stay within rate limits.
    if cached is not None:
        return cached

    url = f"{GITHUB_API_BASE}/users/{username}/gists"
    params = {"page": page, "per_page": per_page}

    async with httpx.AsyncClient() as client: # Create an asynchronous HTTP client to make the request to the GitHub API. httpx.AsyncClient allows us to perform non-blocking I/O operations, improving the performance of our API when handling multiple requests concurrently. async with ensures that the client is properly closed after the request is made, preventing resource leaks.
        response = await client.get(url, headers=GITHUB_HEADERS, params=params)

        if response.status_code == 404: # If the GitHub API returns a 404 status code, it means the specified user does not exist. In this case, we return None to indicate that there are no gists to fetch.
            return None

        response.raise_for_status() # Raise an exception for any HTTP status code that indicates an error (e.g., 403, 500). This allows us to handle these errors gracefully in the calling function and provide appropriate feedback to the client.
        data = response.json()

    _set_cache(key, data)
    return data


def format_gist(raw: dict) -> dict:
    """
    Return a trimmed gist object with only the fields we expose.

    The raw GitHub response contains ~30 fields and represents files as a
    dict keyed by filename. We normalise files to a flat list for consistency.
    """
    return {
        "id": raw["id"],
        "description": raw.get("description") or "No description provided",
        "html_url": raw["html_url"],
        "public": raw["public"],
        "created_at": raw["created_at"],
        "updated_at": raw["updated_at"],
        "comments": raw.get("comments", 0),
        "files": [
            {
                "filename": f["filename"],
                "language": f.get("language"),
                "size": f["size"],
                "raw_url": f["raw_url"],
            }
            for f in raw["files"].values()
        ],
    }