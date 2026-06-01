# GitHub Gists API

A lightweight HTTP API that proxies GitHub's public gists endpoint.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/{username}` | Returns a list of public gists for a GitHub user |
| GET | `/{username}?page=2&per_page=50` | Paginate results (max 100 per page) |
| GET | `/health` | Liveness check |

### Example response — `GET /octocat`

```json
{
  "user": "octocat",
  "page": 1,
  "per_page": 30,
  "count": 8,
  "gists": [
    {
      "id": "6cad326836d38bd3a7ae",
      "description": "Hello world!",
      "html_url": "https://gist.github.com/octocat/6cad326836d38bd3a7ae",
      "public": true,
      "created_at": "2014-10-01T16:19:34Z",
      "updated_at": "2026-04-22T22:17:42Z",
      "comments": 293,
      "files": [
        {
          "filename": "hello_world.rb",
          "language": "Ruby",
          "size": 175,
          "raw_url": "https://gist.githubusercontent.com/octocat/6cad326836d38bd3a7ae/raw/db9c55113504e46fa076e7df3a04ce592e2e86d8/hello_world.rb"
        }
      ]
    }
}
```

## Running with Docker

Requires [Docker](https://docs.docker.com/get-docker/).

```bash
docker build -t gist-api .
docker run -p 8080:8080 gist-api
```

```bash
curl http://localhost:8080/octocat
```

## Running locally

Requires Python 3.10+.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --port 8080
```

## Running the tests

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest test/ -v
```

## Design notes

- **FastAPI** handles routing and automatic query parameter validation
- **httpx** makes async requests to the GitHub API
- **In-memory cache** with a 60-second TTL keeps the app within GitHub's unauthenticated rate limit of 60 requests per hour
- Gist responses are trimmed to a consistent set of fields rather than forwarding GitHub's raw response# test
