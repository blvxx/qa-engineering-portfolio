"""Contract and functional tests for the JSONPlaceholder Posts API."""

import json
from pathlib import Path

import allure
import pytest
from jsonschema import Draft202012Validator, FormatChecker, ValidationError, validate

from api_client import PostsApiClient


SCHEMA_DIR = Path(__file__).parent.parent / "schemas"
POST_SCHEMA = json.loads((SCHEMA_DIR / "post.schema.json").read_text(encoding="utf-8"))
CREATE_POST_SCHEMA = json.loads(
    (SCHEMA_DIR / "post-create-request.schema.json").read_text(encoding="utf-8")
)
COMMENT_SCHEMA = json.loads(
    (SCHEMA_DIR / "comment.schema.json").read_text(encoding="utf-8")
)


@pytest.fixture
def api_client():
    with PostsApiClient() as client:
        yield client


@pytest.fixture
def schema():
    return POST_SCHEMA


@pytest.fixture
def create_post_schema():
    return CREATE_POST_SCHEMA


@pytest.fixture
def comment_schema():
    return COMMENT_SCHEMA


def assert_json_response(response, expected_status=200):
    """Assert the common JSON API response contract."""
    assert response.status_code == expected_status
    content_type = response.headers.get("Content-Type", "")
    assert "application/json" in content_type.lower()


@allure.feature("Posts API")
@allure.story("List posts")
@pytest.mark.smoke
@pytest.mark.contract
def test_get_posts_returns_100_schema_valid_items(api_client, schema):
    response = api_client.get_posts()
    assert_json_response(response)

    posts = response.json()
    assert isinstance(posts, list)
    assert len(posts) == 100

    validator = Draft202012Validator(schema)
    for post in posts:
        validator.validate(post)


@allure.feature("Posts API")
@allure.story("Get post details")
@pytest.mark.smoke
@pytest.mark.contract
def test_get_single_post_has_required_fields_and_schema(api_client, schema):
    response = api_client.get_post(1)
    assert_json_response(response)

    post = response.json()
    assert post["id"] == 1
    Draft202012Validator(schema).validate(post)
    allure.attach(
        json.dumps(post, ensure_ascii=False, indent=2),
        name="post-1-response",
        attachment_type=allure.attachment_type.JSON,
    )


@allure.feature("Posts API")
@allure.story("Valid post IDs")
@pytest.mark.contract
@pytest.mark.parametrize("post_id", [1, 10, 50, 100])
def test_get_post_by_valid_ids(api_client, schema, post_id):
    response = api_client.get_post(post_id)
    assert_json_response(response)

    post = response.json()
    assert post["id"] == post_id
    Draft202012Validator(schema).validate(post)


@allure.feature("Posts API")
@allure.story("Filter posts by user")
@pytest.mark.contract
@pytest.mark.parametrize("user_id", [1, 2, 5, 10])
def test_filter_posts_by_user_id(api_client, schema, user_id):
    response = api_client.get_posts(userId=user_id)
    assert_json_response(response)

    posts = response.json()
    assert posts, f"Expected posts for userId={user_id}"
    assert all(post["userId"] == user_id for post in posts)
    for post in posts:
        Draft202012Validator(schema).validate(post)




@allure.feature("Post relationships")
@allure.story("Retrieve comments for a post")
@pytest.mark.contract
@pytest.mark.parametrize("post_id", [1, 10, 100])
def test_get_post_comments_returns_related_comments(api_client, comment_schema, post_id):
    response = api_client.get_post_comments(post_id)
    assert_json_response(response)

    comments = response.json()
    assert isinstance(comments, list)
    assert len(comments) == 5

    validator = Draft202012Validator(
        comment_schema,
        format_checker=FormatChecker(),
    )
    for comment in comments:
        assert comment["postId"] == post_id
        validator.validate(comment)


@allure.feature("Post relationships")
@allure.story("Unknown parent resource")
@pytest.mark.negative
def test_unknown_post_has_no_related_comments(api_client):
    response = api_client.get_post_comments(999999)
    assert_json_response(response)
    assert response.json() == []

@allure.feature("Posts API")
@allure.story("Create post")
@pytest.mark.crud
@pytest.mark.parametrize(
    "payload",
    [
        {"userId": 1, "title": "API test post", "body": "Created by pytest"},
        {"userId": 2, "title": "Boundary payload", "body": "Second create scenario"},
    ],
)
def test_create_post_returns_created_resource(api_client, schema, create_post_schema, payload):
    Draft202012Validator(create_post_schema).validate(payload)

    response = api_client.create_post(payload)
    assert_json_response(response, expected_status=201)

    created_post = response.json()
    assert created_post["id"] > 0
    assert created_post["userId"] == payload["userId"]
    assert created_post["title"] == payload["title"]
    assert created_post["body"] == payload["body"]
    Draft202012Validator(schema).validate(created_post)
    allure.attach(
        json.dumps({"request": payload, "response": created_post}, ensure_ascii=False, indent=2),
        name="create-post-exchange",
        attachment_type=allure.attachment_type.JSON,
    )


@allure.feature("Posts API")
@allure.story("Replace post with PUT")
@pytest.mark.crud
def test_put_replaces_post_fields(api_client, schema):
    payload = {
        "id": 1,
        "userId": 1,
        "title": "PUT replacement title",
        "body": "PUT replacement body",
    }

    response = api_client.replace_post(1, payload)
    assert_json_response(response)

    updated_post = response.json()
    assert updated_post == payload
    Draft202012Validator(schema).validate(updated_post)


@allure.feature("Posts API")
@allure.story("Partially update post with PATCH")
@pytest.mark.crud
def test_patch_updates_only_requested_field(api_client, schema):
    payload = {"title": "PATCH updated title"}

    response = api_client.patch_post(1, payload)
    assert_json_response(response)

    updated_post = response.json()
    assert updated_post["id"] == 1
    assert updated_post["title"] == payload["title"]
    assert updated_post["body"]
    assert updated_post["userId"] == 1
    Draft202012Validator(schema).validate(updated_post)


@allure.feature("Posts API")
@allure.story("Delete post")
@pytest.mark.crud
@pytest.mark.parametrize("post_id", [1, 10, 100])
def test_delete_post_returns_success(api_client, post_id):
    response = api_client.delete_post(post_id)
    assert response.status_code == 200


@allure.feature("Posts API")
@allure.story("Negative post ID scenarios")
@pytest.mark.negative
@pytest.mark.parametrize("post_id", [0, -1, 999999])
def test_unknown_or_invalid_post_id_returns_404(api_client, post_id):
    response = api_client.get_post(post_id)
    assert_json_response(response, expected_status=404)
    assert response.json() == {}


@allure.feature("Posts API")
@allure.story("Unknown user filter")
@pytest.mark.negative
@pytest.mark.parametrize("user_id", [0, 999, -5])
def test_filter_with_unknown_user_returns_empty_list(api_client, user_id):
    response = api_client.get_posts(userId=user_id)
    assert_json_response(response)
    assert response.json() == []


@allure.feature("JSON Schema")
@allure.story("Schema definitions are valid")
@pytest.mark.unit
def test_post_schema_definition_is_valid(schema, create_post_schema, comment_schema):
    Draft202012Validator.check_schema(schema)
    Draft202012Validator.check_schema(create_post_schema)
    Draft202012Validator.check_schema(comment_schema)


@allure.feature("JSON Schema")
@allure.story("Reject invalid response payloads")
@pytest.mark.unit
@pytest.mark.parametrize(
    "invalid_post",
    [
        {"userId": "not-an-integer", "id": 1, "title": "Title", "body": "Body"},
        {"userId": 1, "id": 0, "title": "Title", "body": "Body"},
        {"userId": 1, "id": 1, "title": "", "body": "Body"},
        {"userId": 1, "id": 1, "title": "Title"},
        {"userId": 1, "id": 1, "title": "Title", "body": "Body", "extra": True},
    ],
)
def test_schema_rejects_invalid_post(schema, invalid_post):
    with pytest.raises(ValidationError):
        validate(instance=invalid_post, schema=schema)


@allure.feature("JSON Schema")
@allure.story("Reject invalid create request payloads")
@pytest.mark.unit
@pytest.mark.parametrize(
    "invalid_payload",
    [
        {"userId": 0, "title": "Title", "body": "Body"},
        {"userId": 1, "title": "", "body": "Body"},
        {"userId": 1, "title": "Title"},
        {"userId": 1, "title": "Title", "body": "Body", "id": 100},
    ],
)
def test_create_request_schema_rejects_invalid_payload(create_post_schema, invalid_payload):
    with pytest.raises(ValidationError):
        validate(instance=invalid_payload, schema=create_post_schema)
