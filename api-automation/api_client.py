"""Reusable HTTP client for the JSONPlaceholder Posts API."""

from __future__ import annotations

import os
from typing import Any, Iterator, Mapping

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class PostsApiClient:
    """Small requests-based client used by the API test suite.

    API_BASE_URL and API_BEARER_TOKEN can be used for environment configuration.
    The owned session retries transient failures only for safe HTTP methods.
    Write methods are deliberately excluded to avoid accidental replays.
    """

    DEFAULT_BASE_URL = "https://jsonplaceholder.typicode.com"
    USER_AGENT = "blvxx-api-automation/1.1"

    def __init__(
        self,
        session: requests.Session | None = None,
        timeout: float = 10.0,
        base_url: str | None = None,
        bearer_token: str | None = None,
        max_retries: int = 2,
        backoff_factor: float = 0.3,
    ) -> None:
        if timeout <= 0:
            raise ValueError("timeout must be greater than zero")
        if max_retries < 0:
            raise ValueError("max_retries cannot be negative")
        if backoff_factor < 0:
            raise ValueError("backoff_factor cannot be negative")

        owns_session = session is None
        self._owns_session = owns_session
        self.session = session if session is not None else requests.Session()
        self.timeout = timeout
        self.base_url = (
            base_url or os.getenv("API_BASE_URL") or self.DEFAULT_BASE_URL
        ).rstrip("/")

        self.session.headers.update(
            {
                "Accept": "application/json",
                "User-Agent": self.USER_AGENT,
            }
        )

        token = bearer_token or os.getenv("API_BEARER_TOKEN")
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"

        if owns_session:
            retry = Retry(
                total=max_retries,
                connect=max_retries,
                read=0,
                status=max_retries,
                backoff_factor=backoff_factor,
                status_forcelist=(429, 500, 502, 503, 504),
                allowed_methods=frozenset({"GET", "HEAD", "OPTIONS"}),
                respect_retry_after_header=True,
                raise_on_status=False,
            )
            adapter = HTTPAdapter(max_retries=retry)
            self.session.mount("http://", adapter)
            self.session.mount("https://", adapter)

    def get_posts(self, **params: Any) -> requests.Response:
        """Return posts, optionally filtered by query parameters."""
        return self.session.get(
            f"{self.base_url}/posts",
            params=params or None,
            timeout=self.timeout,
        )

    def get_post(self, post_id: int) -> requests.Response:
        """Return a post by ID for positive and negative API tests."""
        return self.session.get(
            f"{self.base_url}/posts/{post_id}",
            timeout=self.timeout,
        )

    def get_post_comments(self, post_id: int) -> requests.Response:
        """Return comments related to a post through the nested resource route."""
        return self.session.get(
            f"{self.base_url}/posts/{post_id}/comments",
            timeout=self.timeout,
        )

    def iter_posts(
        self,
        page_size: int = 20,
        max_pages: int = 10,
    ) -> Iterator[dict[str, Any]]:
        """Yield posts page by page, stopping at a short page or max_pages."""
        if page_size < 1:
            raise ValueError("page_size must be greater than zero")
        if max_pages < 1:
            raise ValueError("max_pages must be greater than zero")

        for page in range(1, max_pages + 1):
            response = self.get_posts(_page=page, _limit=page_size)
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, list):
                raise TypeError("Expected a JSON array of posts")
            for item in payload:
                if not isinstance(item, dict):
                    raise TypeError("Each post must be a JSON object")
                yield item
            if len(payload) < page_size:
                break

    def create_post(self, payload: Mapping[str, Any]) -> requests.Response:
        """Send POST /posts with a JSON payload."""
        return self.session.post(
            f"{self.base_url}/posts",
            json=dict(payload),
            timeout=self.timeout,
        )

    def replace_post(
        self, post_id: int, payload: Mapping[str, Any]
    ) -> requests.Response:
        """Send PUT /posts/{id} with a complete replacement payload."""
        return self.session.put(
            f"{self.base_url}/posts/{post_id}",
            json=dict(payload),
            timeout=self.timeout,
        )

    def patch_post(
        self, post_id: int, payload: Mapping[str, Any]
    ) -> requests.Response:
        """Send PATCH /posts/{id} with a partial update payload."""
        return self.session.patch(
            f"{self.base_url}/posts/{post_id}",
            json=dict(payload),
            timeout=self.timeout,
        )

    def delete_post(self, post_id: int) -> requests.Response:
        """Send DELETE /posts/{id}; the demo API simulates the deletion."""
        return self.session.delete(
            f"{self.base_url}/posts/{post_id}",
            timeout=self.timeout,
        )

    def close(self) -> None:
        """Close the HTTP session only when this client created it."""
        if self._owns_session:
            self.session.close()

    def __enter__(self) -> "PostsApiClient":
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        self.close()
