"""Thread-safe in-memory repository for the fictional booking API."""
from __future__ import annotations

from datetime import date
from threading import RLock
from typing import Any


class BookingConflict(Exception):
    """Raised when a requested room/date range is already reserved."""


class IdempotencyConflict(Exception):
    """Raised when an idempotency key is reused with a different payload."""


class BookingStore:
    """Small isolated store; each test gets a fresh instance."""

    def __init__(self) -> None:
        self.rooms: dict[str, dict[str, int]] = {
            "room-101": {"capacity": 2},
            "room-202": {"capacity": 4},
        }
        self.bookings: dict[str, dict[str, Any]] = {}
        self.idempotency: dict[tuple[str, str], tuple[dict[str, Any], str]] = {}
        self._lock = RLock()

    def list_rooms(self) -> list[dict[str, Any]]:
        return [{"id": room_id, **details} for room_id, details in self.rooms.items()]

    def is_available(self, room_id: str, start: date, end: date) -> bool:
        with self._lock:
            return not any(
                item["room_id"] == room_id
                and item["status"] == "confirmed"
                and start < date.fromisoformat(item["end_date"])
                and end > date.fromisoformat(item["start_date"])
                for item in self.bookings.values()
            )

    def create_booking(
        self,
        payload: dict[str, Any],
        owner: str,
        idempotency_key: str | None,
    ) -> tuple[dict[str, Any], bool]:
        """Create atomically; return (record, was_replayed)."""
        with self._lock:
            key = (owner, idempotency_key) if idempotency_key else None
            if key and key in self.idempotency:
                previous_payload, booking_id = self.idempotency[key]
                if previous_payload != payload:
                    raise IdempotencyConflict
                return self.bookings[booking_id].copy(), True

            start = date.fromisoformat(payload["start_date"])
            end = date.fromisoformat(payload["end_date"])
            if not self.is_available(payload["room_id"], start, end):
                raise BookingConflict

            booking_id = f"booking-{len(self.bookings) + 1}"
            record = {
                "id": booking_id,
                **payload,
                "status": "confirmed",
                "owner": owner,
            }
            self.bookings[booking_id] = record
            if key:
                self.idempotency[key] = (payload.copy(), booking_id)
            return record.copy(), False

    def get_booking(self, booking_id: str, owner: str) -> dict[str, Any] | None:
        with self._lock:
            record = self.bookings.get(booking_id)
            if record is None or record["owner"] != owner:
                return None
            return record.copy()

    def cancel_booking(self, booking_id: str, owner: str) -> dict[str, Any] | None:
        with self._lock:
            record = self.bookings.get(booking_id)
            if record is None or record["owner"] != owner:
                return None
            record["status"] = "cancelled"
            return record.copy()
