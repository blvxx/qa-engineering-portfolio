"""Unit tests for the reusable API client (no network calls)."""

from unittest.mock import Mock

import pytest
import requests

from api_client import PostsApiClient


pytestmark = pytest.mark.unit


def make_session():
    session = Mock(spec=requests.Session)
    session.headers = {}
    return session


def test_client_sets_default_headers_and_timeout():
    session = make_session()
    client = PostsApiClient(session=session, timeout=4)

    assert session.headers["Accept"] == "application/json"
    assert session.headers["User-Agent"] == PostsApiClient.USER_AGENT
    assert client.timeout == 4
    assert client.base_url == PostsApiClient.DEFAULT_BASE_URL


def test_environment_variable_overrides_default_base_url(monkeypatch):
    monkeypatch.setenv("API_BASE_URL", "https://staging.example.test/")

    client = PostsApiClient(session=make_session())

    assert client.base_url == "https://staging.example.test"


def test_get_posts_passes_query_params_and_timeout():
    session = make_session()
    expected_response = object()
    session.get.return_value = expected_response
    client = PostsApiClient(
        session=session,
        timeout=3,
        base_url="https://api.example.test/",
    )

    response = client.get_posts(userId=2)

    assert response is expected_response
    session.get.assert_called_once_with(
        "https://api.example.test/posts",
        params={"userId": 2},
        timeout=3,
    )


def test_get_posts_without_filters_uses_no_query_params():
    session = make_session()
    client = PostsApiClient(session=session)

    client.get_posts()

    session.get.assert_called_once_with(
        "https://jsonplaceholder.typicode.com/posts",
        params=None,
        timeout=10.0,
    )


def test_get_post_builds_expected_resource_url():
    session = make_session()
    client = PostsApiClient(
        session=session,
        base_url="https://api.example.test",
    )

    client.get_post(42)

    session.get.assert_called_once_with(
        "https://api.example.test/posts/42",
        timeout=10.0,
    )


def test_create_post_sends_json_payload():
    session = make_session()
    client = PostsApiClient(session=session, timeout=5)
    payload = {"userId": 1, "title": "Title", "body": "Body"}

    client.create_post(payload)

    session.post.assert_called_once_with(
        "https://jsonplaceholder.typicode.com/posts",
        json=payload,
        timeout=5,
    )


def test_put_replaces_post_with_full_json_payload():
    session = make_session()
    client = PostsApiClient(session=session)
    payload = {"id": 7, "userId": 2, "title": "New title", "body": "New body"}

    client.replace_post(7, payload)

    session.put.assert_called_once_with(
        "https://jsonplaceholder.typicode.com/posts/7",
        json=payload,
        timeout=10.0,
    )


def test_patch_sends_partial_json_payload():
    session = make_session()
    client = PostsApiClient(session=session)
    payload = {"title": "Updated title"}

    client.patch_post(12, payload)

    session.patch.assert_called_once_with(
        "https://jsonplaceholder.typicode.com/posts/12",
        json=payload,
        timeout=10.0,
    )


def test_delete_uses_expected_resource_url():
    session = make_session()
    client = PostsApiClient(session=session)

    client.delete_post(15)

    session.delete.assert_called_once_with(
        "https://jsonplaceholder.typicode.com/posts/15",
        timeout=10.0,
    )


@pytest.mark.parametrize("timeout", [0, -1, -0.5])
def test_client_rejects_non_positive_timeout(timeout):
    with pytest.raises(ValueError, match="timeout must be greater than zero"):
        PostsApiClient(session=make_session(), timeout=timeout)


def test_transport_timeout_is_not_silently_swallowed():
    session = make_session()
    session.get.side_effect = requests.Timeout("request timed out")
    client = PostsApiClient(session=session)

    with pytest.raises(requests.Timeout, match="request timed out"):
        client.get_post(1)


def test_context_manager_does_not_close_borrowed_session():
    session = make_session()

    with PostsApiClient(session=session):
        pass

    session.close.assert_not_called()


def test_context_manager_closes_owned_session(monkeypatch):
    session = make_session()
    monkeypatch.setattr(requests, "Session", lambda: session)

    with PostsApiClient():
        pass

    session.close.assert_called_once_with()


def test_get_post_comments_builds_nested_resource_url():
    session = make_session()
    client = PostsApiClient(
        session=session,
        base_url="https://api.example.test",
    )

    client.get_post_comments(42)

    session.get.assert_called_once_with(
        "https://api.example.test/posts/42/comments",
        timeout=10.0,
    )
