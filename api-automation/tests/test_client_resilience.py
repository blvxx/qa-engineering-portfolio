from __future__ import annotations

import os
import unittest
from unittest.mock import patch

import requests

from api_client import PostsApiClient


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self, pages):
        self.headers = {}
        self.pages = pages
        self.calls = []
        self.closed = False

    def get(self, url, params=None, timeout=None):
        self.calls.append({"url": url, "params": params, "timeout": timeout})
        page = (params or {}).get("_page", 1)
        return FakeResponse(self.pages.get(page, []))

    def close(self):
        self.closed = True


class ClientResilienceTests(unittest.TestCase):
    def test_bearer_token_is_added_from_constructor(self):
        client = PostsApiClient(session=FakeSession({}), bearer_token="demo-token")
        self.assertEqual(client.session.headers["Authorization"], "Bearer demo-token")

    def test_bearer_token_can_be_read_from_environment(self):
        with patch.dict(os.environ, {"API_BEARER_TOKEN": "env-token"}):
            client = PostsApiClient(session=FakeSession({}))
        self.assertEqual(client.session.headers["Authorization"], "Bearer env-token")

    def test_authorization_header_is_omitted_when_token_is_not_configured(self):
        client = PostsApiClient(session=FakeSession({}))
        self.assertNotIn("Authorization", client.session.headers)

    def test_owned_session_retries_only_safe_http_methods(self):
        client = PostsApiClient(max_retries=3, backoff_factor=0.1)
        adapter = client.session.get_adapter("https://")
        self.assertEqual(adapter.max_retries.total, 3)
        self.assertIn("GET", adapter.max_retries.allowed_methods)
        self.assertNotIn("POST", adapter.max_retries.allowed_methods)
        client.close()

    def test_invalid_retry_configuration_is_rejected(self):
        with self.assertRaises(ValueError):
            PostsApiClient(session=FakeSession({}), max_retries=-1)
        with self.assertRaises(ValueError):
            PostsApiClient(session=FakeSession({}), backoff_factor=-0.1)

    def test_iter_posts_uses_pagination_and_stops_on_short_page(self):
        session = FakeSession({
            1: [{"id": 1}, {"id": 2}],
            2: [{"id": 3}],
        })
        client = PostsApiClient(session=session)
        results = list(client.iter_posts(page_size=2, max_pages=10))
        self.assertEqual([item["id"] for item in results], [1, 2, 3])
        self.assertEqual([call["params"]["_page"] for call in session.calls], [1, 2])

    def test_iter_posts_respects_max_pages(self):
        session = FakeSession({
            1: [{"id": 1}],
            2: [{"id": 2}],
            3: [{"id": 3}],
        })
        client = PostsApiClient(session=session)
        results = list(client.iter_posts(page_size=1, max_pages=2))
        self.assertEqual([item["id"] for item in results], [1, 2])

    def test_iter_posts_validates_page_arguments(self):
        client = PostsApiClient(session=FakeSession({}))
        with self.assertRaises(ValueError):
            list(client.iter_posts(page_size=0))
        with self.assertRaises(ValueError):
            list(client.iter_posts(max_pages=0))


if __name__ == "__main__":
    unittest.main()
