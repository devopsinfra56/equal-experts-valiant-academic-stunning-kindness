import httpx # Used to test HTTP requests to the GitHub API.
from fastapi import FastAPI, HTTPException, Query # FastAPI framework for building the API and handling HTTP exceptions.
import json # Used for parsing JSON responses from the GitHub API.
from prometheus_fastapi_instrumentator import Instrumentator # Used to expose Prometheus metrics for monitoring the API.    
from app.github import get_user_gists, format_gist # Used to fetch and format gists from GitHub.


# title, description, and version appear at /docs in the auto-generated
# Swagger UI — a free interactive documentation page FastAPI builds for you
app = FastAPI(
    title="GitHub Gists API",
    description="Returns a GitHub user's public gists. Usage: GET /{username}",
)

Instrumentator().instrument(app).expose(app)  # Set up Prometheus metrics for monitoring the API.

# /health must be declared before /{username} so FastAPI matches it
# before the wildcard route.
@app.get("/health")
async def health_check(): # Simple health check endpoint to verify the API is running.
    return {"status": "ok"} # Returns a simple JSON response indicating the API is healthy.


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
        raise HTTPException(status_code=503, detail="Could not reach the GitHub API.")
    except json.JSONDecodeError:
        # Handle cases where GitHub returns a non-JSON error page (e.g. 500 HTML response)
        raise HTTPException(status_code=502, detail="Invalid response from GitHub API.")

    if raw_gists is None:
        raise HTTPException(status_code=404, detail=f"GitHub user '{username}' not found.") # Handle the case where the specified GitHub user does not exist.

    return {
        "user": username,
        "page": page,
        "per_page": per_page,
        "count": len(raw_gists),
        "gists": [format_gist(g) for g in raw_gists],
    }