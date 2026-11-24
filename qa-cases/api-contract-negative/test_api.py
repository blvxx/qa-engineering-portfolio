from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app import create_app
from store import BookingStore


@pytest.fixture
def client() -> TestClient:
    """A fresh application and repository isolate every test."""
    return TestClient(create_app(BookingStore()))


def booking_payload(**overrides: object) -> dict:
    body = {
        "room_id": "room-101",
        "start_date": "2027-03-12",
        "end_date": "2027-03-15",
        "guests": 2,
        "guest": {"name": "Test Guest", "email": "qa@example.com"},
    }
    body.update(overrides)
    return body


AUTH_A = {"Authorization": "Bearer user-a"}
AUTH_B = {"Authorization": "Bearer user-b"}


def create_booking(client: TestClient, **kwargs: object) -> dict:
    response = client.post("/v1/bookings", json=booking_payload(**kwargs), headers=AUTH_A)
    assert response.status_code == 201, response.text
    return response.json()


def test_health_endpoint_is_available(client: TestClient) -> None:
    response = client.get("/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_rooms_contract_contains_pagination_metadata(client: TestClient) -> None:
    response = client.get("/v1/rooms")
    assert response.status_code == 200
    body = response.json()
    assert {"items", "page", "limit", "total"} == set(body)
    assert body["total"] == 2
    assert len(body["items"]) == 2


def test_rooms_pagination_returns_requested_page_size(client: TestClient) -> None:
    response = client.get("/v1/rooms", params={"page": 1, "limit": 1})
    assert response.status_code == 200
    assert len(response.json()["items"]) == 1
    assert response.json()["total"] == 2


@pytest.mark.parametrize("params", [{"page": 0}, {"limit": 0}, {"limit": 101}])
def test_invalid_pagination_is_rejected(client: TestClient, params: dict) -> None:
    assert client.get("/v1/rooms", params=params).status_code == 422


def test_availability_for_unknown_room_returns_404(client: TestClient) -> None:
    response = client.get("/v1/availability", params={
        "room_id": "unknown", "start_date": "2027-03-12", "end_date": "2027-03-15"
    })
    assert response.status_code == 404


@pytest.mark.parametrize(
    ("start", "end"),
    [("2027-03-15", "2027-03-12"), ("2027-03-12", "2027-03-12")],
)
def test_invalid_availability_range_is_rejected(client: TestClient, start: str, end: str) -> None:
    response = client.get("/v1/availability", params={
        "room_id": "room-101", "start_date": start, "end_date": end
    })
    assert response.status_code == 422


def test_create_booking_returns_contract_fields(client: TestClient) -> None:
    response = client.post("/v1/bookings", json=booking_payload(), headers=AUTH_A)
    assert response.status_code == 201
    assert set(response.json()) == {
        "id", "room_id", "start_date", "end_date", "guests", "guest", "status"
    }
    assert response.json()["status"] == "confirmed"


def test_create_booking_requires_authentication(client: TestClient) -> None:
    assert client.post("/v1/bookings", json=booking_payload()).status_code == 401


def test_unknown_token_is_rejected(client: TestClient) -> None:
    response = client.post(
        "/v1/bookings", json=booking_payload(), headers={"Authorization": "Bearer expired-token"}
    )
    assert response.status_code == 401


@pytest.mark.parametrize(
    "payload",
    [
        {"start_date": "2027-03-16"},
        {"guests": 0},
        {"guests": -1},
        {"guest": {"name": "", "email": "qa@example.com"}},
        {"guest": {"name": "Guest", "email": "not-an-email"}},
        {"guest": {"name": "Guest", "email": "qa@example.com", "admin": True}},
    ],
)
def test_invalid_booking_payload_is_rejected(client: TestClient, payload: dict) -> None:
    assert client.post("/v1/bookings", json=booking_payload(**payload), headers=AUTH_A).status_code == 422


def test_unknown_room_booking_returns_404(client: TestClient) -> None:
    response = client.post("/v1/bookings", json=booking_payload(room_id="missing"), headers=AUTH_A)
    assert response.status_code == 404


def test_booking_over_room_capacity_is_rejected(client: TestClient) -> None:
    response = client.post("/v1/bookings", json=booking_payload(guests=3), headers=AUTH_A)
    assert response.status_code == 422


def test_overlapping_booking_returns_conflict_and_does_not_create_duplicate(client: TestClient) -> None:
    create_booking(client)
    response = client.post(
        "/v1/bookings",
        json=booking_payload(start_date="2027-03-14", end_date="2027-03-17"),
        headers={**AUTH_A, "Idempotency-Key": "overlap-2"},
    )
    assert response.status_code == 409
    assert "unavailable" in response.json()["detail"]


def test_adjacent_non_overlapping_booking_is_allowed(client: TestClient) -> None:
    create_booking(client)
    response = client.post(
        "/v1/bookings",
        json=booking_payload(start_date="2027-03-15", end_date="2027-03-18"),
        headers={**AUTH_A, "Idempotency-Key": "adjacent-2"},
    )
    assert response.status_code == 201


def test_availability_changes_after_booking(client: TestClient) -> None:
    create_booking(client)
    response = client.get("/v1/availability", params={
        "room_id": "room-101", "start_date": "2027-03-13", "end_date": "2027-03-14"
    })
    assert response.status_code == 200
    assert response.json()["available"] is False


def test_idempotent_retry_returns_same_booking_and_replay_header(client: TestClient) -> None:
    headers = {**AUTH_A, "Idempotency-Key": "retry-001"}
    first = client.post("/v1/bookings", json=booking_payload(), headers=headers)
    second = client.post("/v1/bookings", json=booking_payload(), headers=headers)
    assert first.status_code == 201
    assert second.status_code == 200
    assert first.json()["id"] == second.json()["id"]
    assert second.headers["Idempotency-Replayed"] == "true"


def test_reusing_idempotency_key_with_different_payload_returns_409(client: TestClient) -> None:
    headers = {**AUTH_A, "Idempotency-Key": "same-key"}
    client.post("/v1/bookings", json=booking_payload(), headers=headers)
    changed = client.post("/v1/bookings", json=booking_payload(guests=1), headers=headers)
    assert changed.status_code == 409


def test_idempotency_keys_are_scoped_to_authenticated_user(client: TestClient) -> None:
    key = {"Idempotency-Key": "same-key"}
    first = client.post("/v1/bookings", json=booking_payload(), headers={**AUTH_A, **key})
    second = client.post(
        "/v1/bookings",
        json=booking_payload(room_id="room-202"),
        headers={**AUTH_B, **key},
    )
    assert first.status_code == 201
    assert second.status_code == 201


def test_owner_can_read_booking_but_another_user_cannot(client: TestClient) -> None:
    booking = create_booking(client)
    assert client.get(f"/v1/bookings/{booking['id']}", headers=AUTH_A).status_code == 200
    response = client.get(f"/v1/bookings/{booking['id']}", headers=AUTH_B)
    assert response.status_code == 404
    assert "guest" not in response.json()


def test_booking_lookup_requires_authentication(client: TestClient) -> None:
    assert client.get("/v1/bookings/booking-1").status_code == 401


def test_cancel_booking_is_idempotent_and_releases_availability(client: TestClient) -> None:
    booking = create_booking(client)
    url = f"/v1/bookings/{booking['id']}"
    first = client.delete(url, headers=AUTH_A)
    second = client.delete(url, headers=AUTH_A)
    assert first.status_code == second.status_code == 200
    assert second.json()["status"] == "cancelled"
    availability = client.get("/v1/availability", params={
        "room_id": "room-101", "start_date": "2027-03-12", "end_date": "2027-03-15"
    })
    assert availability.json()["available"] is True


def test_another_user_cannot_cancel_booking(client: TestClient) -> None:
    booking = create_booking(client)
    response = client.delete(f"/v1/bookings/{booking['id']}", headers=AUTH_B)
    assert response.status_code == 404


def test_unknown_booking_returns_404(client: TestClient) -> None:
    assert client.get("/v1/bookings/missing", headers=AUTH_A).status_code == 404
