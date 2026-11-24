# Request / Response Examples — Booking API Sandbox

These examples document the **implemented local sandbox contract**. They are not captured from a third-party or production service.

## 1. Create a booking

```http
POST /v1/bookings
Authorization: Bearer user-a
Idempotency-Key: booking-qa-001
Content-Type: application/json
```

```json
{
  "room_id": "room-101",
  "start_date": "2027-03-12",
  "end_date": "2027-03-15",
  "guests": 2,
  "guest": {
    "name": "Test Guest",
    "email": "qa@example.com"
  }
}
```

First submission: `201 Created`. Response shape:

```json
{
  "id": "booking-1",
  "room_id": "room-101",
  "start_date": "2027-03-12",
  "end_date": "2027-03-15",
  "guests": 2,
  "guest": {
    "name": "Test Guest",
    "email": "qa@example.com"
  },
  "status": "confirmed"
}
```

## 2. Retry with the same key and identical body

The sandbox returns `200 OK`, the original booking, and header:

```http
Idempotency-Replayed: true
```

The request must not create a second booking.

## 3. Validation failure

Reversed or zero-length dates return `422 Unprocessable Entity`. Pydantic schema violations (for example, malformed email or unexpected fields) also return 422.

Example application-level error:

```json
{
  "detail": "start_date must be before end_date"
}
```

Schema validation errors use FastAPI's structured `detail` array.

## 4. Booking conflict

A second booking for an overlapping interval in the same room returns `409 Conflict`:

```json
{
  "detail": "room unavailable for requested dates"
}
```

Adjacent intervals are allowed because date ranges follow the half-open convention `[start_date, end_date)`.

## 5. Authorization and privacy

- Missing or unknown token: `401 Unauthorized`.
- A user reading or cancelling another user's booking receives privacy-safe `404 Not Found`.
- The sandbox's Bearer tokens are test fixtures, not real authentication.

## 6. Explore the contract

When the app is running locally, the interactive OpenAPI document is available at `/docs`; the schema is available at `/openapi.json`.
