"""
Tests for the GitHub Gists API.

Uses FastAPI's TestClient (synchronous) with unittest.mock to avoid
real GitHub API calls — keeping tests fast, deterministic, and offline.

Note: get_user_gists is patched at "app.main.get_user_gists" (where it is
*used*) rather than "app.github.get_user_gists" (where it is *defined*),
because Python resolves the name at import time.
"""

from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

# Shared test dataL A fake git that mirrors the structure of GitHub's API responses.
SAMPLE_GIST = {
    "id": "aa5a315d61ae9438b18d",
    "description": "Hello World Examples",
    "html_url": "https://gist.github.com/octocat/aa5a315d61ae9438b18d",
    "public": True,
    "created_at": "2010-04-14T02:15:15Z",
    "updated_at": "2011-06-20T11:34:15Z",
    "comments": 0,
    "files": {
        "hello_world.rb": {
            "filename": "hello_world.rb",
            "language": "Ruby",
            "size": 167,
            "raw_url": "https://gist.githubusercontent.com/octocat/aa5a315d/raw/hello_world.rb",
            "type": "application/x-ruby",
        }
    },
}


class TestListUserGists:

    def test_valid_user_returns_gist_list(self):
        with patch("app.main.get_user_gists", new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = [SAMPLE_GIST]
            response = client.get("/octocat")

        assert response.status_code == 200
        data = response.json()
        assert data["user"] == "octocat"
        assert data["count"] == 1
        assert data["page"] == 1
        assert data["per_page"] == 30

        gist = data["gists"][0]
        assert gist["id"] == "aa5a315d61ae9438b18d"
        assert gist["description"] == "Hello World Examples"
        assert gist["files"][0]["filename"] == "hello_world.rb"

    def test_unknown_user_returns_404(self):
        with patch("app.main.get_user_gists", new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = None
            response = client.get("/nonexistent_user_xyz")

        assert response.status_code == 404

    def test_user_with_no_gists_returns_empty_list(self):
        """A valid user with zero gists should return 200, not 404."""
        with patch("app.main.get_user_gists", new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = []
            response = client.get("/octocat")

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["gists"] == []

    def test_pagination_params_are_forwarded(self):
        with patch("app.main.get_user_gists", new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = [SAMPLE_GIST]
            response = client.get("/octocat?page=3&per_page=10")

        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 3
        assert data["per_page"] == 10
        mock_fn.assert_called_once_with("octocat", page=3, per_page=10)

    def test_invalid_page_returns_422(self):
        response = client.get("/octocat?page=0")
        assert response.status_code == 422

    def test_per_page_above_100_returns_422(self):
        response = client.get("/octocat?per_page=101")
        assert response.status_code == 422

    def test_null_description_gets_placeholder(self):
        gist_no_desc = {**SAMPLE_GIST, "description": None}
        with patch("app.main.get_user_gists", new_callable=AsyncMock) as mock_fn:
            mock_fn.return_value = [gist_no_desc]
            response = client.get("/octocat")

        assert response.json()["gists"][0]["description"] == "No description provided"


class TestHealthCheck:

    def test_health_returns_ok(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}