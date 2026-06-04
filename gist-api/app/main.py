import httpx # Used to test HTTP requests to the GitHub API.
from fastapi import FastAPI, HTTPException, Query # FastAPI framework for building the API and handling HTTP exceptions.
from json import JSONDecodeError # Used to handle JSON decoding errors when parsing GitHub API responses.
from app.github import get_user_gists, format_gist # Used to fetch and format gists from GitHub.


# title, description, and version appear at /docs in the auto-generated
# Swagger UI — a free interactive documentation page FastAPI builds for you
app = FastAPI(
    title="GitHub Gists API",
    description="Returns a GitHub user's public gists. Usage: GET /{username}",
)

# /health must be declared before /{username} so FastAPI matches it
# before the wildcard route.
@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/{username}")
async def list_user_gists(
    username: str,
    page: int = Query(default=1, ge=1, description="Page number"),
    per_page: int = Query(default=30, ge=1, le=100, description="Results per page (max 100)"),
):
    """Return the public gists for a GitHub user."""
    try:
        raw_gists = await get_user_gists(username, page=page, per_page=per_page)
    except httpx.HTTPStatusError as exc: # Handle HTTP errors returned by the GitHub API (e.g., 403 rate limit, 500 server error).
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"GitHub API error: {exc.response.text}",
        )
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Could not reach the GitHub API.") # Handle network errors when trying to reach the GitHub API.
    except JSONDecodeError:
        raise HTTPException(status_code=502, detail="Invalid response from GitHub API.") # Handle cases where the GitHub API returns a response that cannot be parsed as JSON.

    if raw_gists is None:
        raise HTTPException(status_code=404, detail=f"GitHub user '{username}' not found.") # Handle the case where the specified GitHub user does not exist.

    return {
        "user": username,
        "page": page,
        "per_page": per_page,
        "count": len(raw_gists),
        "gists": [format_gist(g) for g in raw_gists],
    }