"""Fictional booking API used as a deterministic local QA target."""
from __future__ import annotations

from datetime import date
from typing import Annotated

from fastapi import FastAPI, Header, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from store import BookingConflict, BookingStore, IdempotencyConflict


class Guest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr


class BookingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    room_id: str = Field(min_length=1)
    start_date: date
    end_date: date
    guests: int = Field(ge=1, le=8)
    guest: Guest


class BookingResponse(BaseModel):
    id: str
    room_id: str
    start_date: date
    end_date: date
    guests: int
    guest: Guest
    status: str


class RoomResponse(BaseModel):
    id: str
    capacity: int


class RoomPage(BaseModel):
    items: list[RoomResponse]
    page: int
    limit: int
    total: int


def current_user(authorization: str | None) -> str:
    """Resolve a known sandbox token; this is deliberately not production auth."""
    users = {"Bearer user-a": "user-a", "Bearer user-b": "user-b"}
    if authorization not in users:
        raise HTTPException(status_code=401, detail="unauthorized")
    return users[authorization]


def create_app(store: BookingStore | None = None) -> FastAPI:
    app = FastAPI(
        title="Booking API QA Sandbox",
        description="Fictional service for portfolio-level API contract and negative testing.",
        version="1.0.0",
        openapi_tags=[
            {"name": "catalog", "description": "Room catalogue and availability"},
            {"name": "bookings", "description": "Booking lifecycle and access control"},
        ],
    )
    app.state.store = store or BookingStore()

    @app.get("/v1/health", tags=["catalog"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/v1/rooms", response_model=RoomPage, tags=["catalog"])
    def list_rooms(
        request: Request,
        page: Annotated[int, Field(ge=1)] = 1,
        limit: Annotated[int, Field(ge=1, le=100)] = 20,
    ) -> dict:
        items = request.app.state.store.list_rooms()
        start = (page - 1) * limit
        return {"items": items[start : start + limit], "page": page, "limit": limit, "total": len(items)}

    @app.get("/v1/availability", tags=["catalog"])
    def availability(
        request: Request,
        room_id: str,
        start_date: date,
        end_date: date,
    ) -> dict[str, bool | str]:
        if start_date >= end_date:
            raise HTTPException(status_code=422, detail="start_date must be before end_date")
        if room_id not in request.app.state.store.rooms:
            raise HTTPException(status_code=404, detail="room not found")
        available = request.app.state.store.is_available(room_id, start_date, end_date)
        return {"room_id": room_id, "available": available}

    @app.post("/v1/bookings", response_model=BookingResponse, status_code=201, tags=["bookings"])
    def create_booking(
        payload: BookingRequest,
        request: Request,
        response: Response,
        authorization: Annotated[str | None, Header()] = None,
        idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key", min_length=1, max_length=128)] = None,
    ) -> dict:
        owner = current_user(authorization)
        if payload.start_date >= payload.end_date:
            raise HTTPException(status_code=422, detail="start_date must be before end_date")
        store: BookingStore = request.app.state.store
        room = store.rooms.get(payload.room_id)
        if room is None:
            raise HTTPException(status_code=404, detail="room not found")
        if payload.guests > room["capacity"]:
            raise HTTPException(status_code=422, detail="guest count exceeds room capacity")
        payload_data = payload.model_dump(mode="json")
        try:
            record, replayed = store.create_booking(payload_data, owner, idempotency_key)
        except BookingConflict:
            raise HTTPException(status_code=409, detail="room unavailable for requested dates")
        except IdempotencyConflict:
            raise HTTPException(status_code=409, detail="idempotency key reused with a different payload")
        if replayed:
            response.status_code = 200
            response.headers["Idempotency-Replayed"] = "true"
        return record

    @app.get("/v1/bookings/{booking_id}", response_model=BookingResponse, tags=["bookings"])
    def get_booking(
        booking_id: str,
        request: Request,
        authorization: Annotated[str | None, Header()] = None,
    ) -> dict:
        owner = current_user(authorization)
        record = request.app.state.store.get_booking(booking_id, owner)
        if record is None:
            # Deliberately hide whether another user's booking exists.
            raise HTTPException(status_code=404, detail="booking not found")
        return record

    @app.delete("/v1/bookings/{booking_id}", response_model=BookingResponse, tags=["bookings"])
    def cancel_booking(
        booking_id: str,
        request: Request,
        authorization: Annotated[str | None, Header()] = None,
    ) -> dict:
        owner = current_user(authorization)
        record = request.app.state.store.cancel_booking(booking_id, owner)
        if record is None:
            raise HTTPException(status_code=404, detail="booking not found")
        return record

    return app


app = create_app()
