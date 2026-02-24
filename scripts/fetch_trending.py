#!/usr/bin/env python3
"""
Fetch trending AI skill/agent projects from GitHub.
Searches for repositories related to AI agents, skills, and related topics.
"""

import json
import os
import sys
from datetime import datetime, timezone
from typing import Any
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

GITHUB_API_BASE = "https://api.github.com"

SEARCH_QUERIES = [
    "ai-agent",
    "llm-agent",
    "ai-skill",
    "claude-skill",
    "gpt-agent",
    "autonomous-agent",
    "ai-assistant",
    "langchain-agent",
    "autogpt",
    "agent-framework",
]

TOPICS = [
    "ai-agent",
    "llm",
    "gpt",
    "claude",
    "autonomous-agent",
    "ai-assistant",
    "langchain",
    "openai",
    "anthropic",
]

def get_github_token() -> str | None:
    return os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")

def make_request(url: str, token: str | None = None) -> dict[str, Any]:
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "GitHub-AI-Trending-Fetcher/1.0",
    }
    if token:
        headers["Authorization"] = f"token {token}"
    
    request = Request(url, headers=headers)
    try:
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        if e.code == 403:
            print(f"Rate limit exceeded. Try again later or use a token.", file=sys.stderr)
        raise
    except URLError as e:
        print(f"Network error: {e}", file=sys.stderr)
        raise

def search_repositories(query: str, token: str | None = None, sort: str = "stars", order: str = "desc", per_page: int = 30) -> list[dict]:
    url = f"{GITHUB_API_BASE}/search/repositories?q={query}&sort={sort}&order={order}&per_page={per_page}"
    result = make_request(url, token)
    return result.get("items", [])

def get_trending_by_topic(topic: str, token: str | None = None, per_page: int = 20) -> list[dict]:
    url = f"{GITHUB_API_BASE}/search/repositories?q=topic:{topic}&sort=stars&order=desc&per_page={per_page}"
    result = make_request(url, token)
    return result.get("items", [])

def normalize_repo(repo: dict) -> dict:
    return {
        "id": repo.get("id"),
        "name": repo.get("name"),
        "full_name": repo.get("full_name"),
        "description": repo.get("description", ""),
        "html_url": repo.get("html_url"),
        "stargazers_count": repo.get("stargazers_count", 0),
        "forks_count": repo.get("forks_count", 0),
        "open_issues_count": repo.get("open_issues_count", 0),
        "watchers_count": repo.get("watchers_count", 0),
        "language": repo.get("language"),
        "topics": repo.get("topics", []),
        "created_at": repo.get("created_at"),
        "updated_at": repo.get("updated_at"),
        "pushed_at": repo.get("pushed_at"),
        "owner": {
            "login": repo.get("owner", {}).get("login"),
            "avatar_url": repo.get("owner", {}).get("avatar_url"),
            "type": repo.get("owner", {}).get("type"),
        },
        "license": repo.get("license", {}).get("spdx_id") if repo.get("license") else None,
        "homepage": repo.get("homepage"),
        "archived": repo.get("archived", False),
        "fork": repo.get("fork", False),
    }

def deduplicate_repos(repos: list[dict]) -> list[dict]:
    seen = set()
    unique = []
    for repo in repos:
        full_name = repo.get("full_name")
        if full_name and full_name not in seen:
            seen.add(full_name)
            unique.append(repo)
    return unique

def fetch_all_trending(token: str | None = None) -> dict[str, Any]:
    all_repos = []
    
    print("Fetching repositories by search queries...", file=sys.stderr)
    for query in SEARCH_QUERIES:
        try:
            repos = search_repositories(query, token, per_page=20)
            all_repos.extend(repos)
            print(f"  Query '{query}': found {len(repos)} repos", file=sys.stderr)
        except Exception as e:
            print(f"  Query '{query}' failed: {e}", file=sys.stderr)
    
    print("Fetching repositories by topics...", file=sys.stderr)
    for topic in TOPICS:
        try:
            repos = get_trending_by_topic(topic, token, per_page=15)
            all_repos.extend(repos)
            print(f"  Topic '{topic}': found {len(repos)} repos", file=sys.stderr)
        except Exception as e:
            print(f"  Topic '{topic}' failed: {e}", file=sys.stderr)
    
    normalized = [normalize_repo(r) for r in all_repos]
    unique = deduplicate_repos(normalized)
    
    unique.sort(key=lambda x: x.get("stargazers_count", 0), reverse=True)
    
    return {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "total_count": len(unique),
        "repositories": unique,
    }

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Fetch trending AI skill/agent projects from GitHub")
    parser.add_argument("-o", "--output", default="trending.json", help="Output JSON file path")
    parser.add_argument("-l", "--limit", type=int, default=100, help="Maximum number of repositories to include")
    args = parser.parse_args()
    
    token = get_github_token()
    if not token:
        print("Warning: No GITHUB_TOKEN or GH_TOKEN environment variable set. Rate limits may apply.", file=sys.stderr)
    
    data = fetch_all_trending(token)
    
    data["repositories"] = data["repositories"][:args.limit]
    data["total_count"] = len(data["repositories"])
    
    output_path = os.path.abspath(args.output)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\nFetched {data['total_count']} repositories", file=sys.stderr)
    print(f"Output saved to: {output_path}", file=sys.stderr)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
