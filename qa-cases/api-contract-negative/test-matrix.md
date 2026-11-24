# REST API Test Strategy & Traceability Matrix

**System:** Booking API QA Sandbox  
**Test level:** API / integration (in-process HTTP client)  
**Test type:** Contract, positive, negative, boundary, authorization, state transition  
**Execution:** Local pytest and GitHub Actions

This matrix maps observable API requirements to automated tests. The test suite is the executable source of truth; this document is the readable coverage index.

| Requirement | Risk | Scenario | Automated test |
|---|---|---|---|
| API health is observable | P2 | Health endpoint responds | `test_health_endpoint_is_available` |
| Room catalogue has stable paging contract | P1 | Metadata and page size | `test_rooms_contract_contains_pagination_metadata`, `test_rooms_pagination_returns_requested_page_size` |
| Pagination boundaries are validated | P1 | Zero and excessive values | `test_invalid_pagination_is_rejected` |
| Availability validates resource and date range | P1 | Unknown room, reversed and zero-length dates | `test_availability_for_unknown_room_returns_404`, `test_invalid_availability_range_is_rejected` |
| Booking creation returns a defined contract | P1 | Valid create | `test_create_booking_returns_contract_fields` |
| Booking requires a known identity | P0 | Missing and unknown token | `test_create_booking_requires_authentication`, `test_unknown_token_is_rejected` |
| Invalid request data is rejected | P1 | Date, guest count, email, extra fields | `test_invalid_booking_payload_is_rejected` |
| Room and capacity constraints are enforced | P1 | Unknown room and over-capacity guests | `test_unknown_room_booking_returns_404`, `test_booking_over_room_capacity_is_rejected` |
| Reservations cannot overlap | P0 | Overlap rejected; adjacent interval allowed | `test_overlapping_booking_returns_conflict_and_does_not_create_duplicate`, `test_adjacent_non_overlapping_booking_is_allowed` |
| Availability reflects current reservation state | P1 | Reserved slot becomes unavailable | `test_availability_changes_after_booking` |
| Retry does not create a duplicate | P0 | Same key and same payload | `test_idempotent_retry_returns_same_booking_and_replay_header` |
| Idempotency misuse is rejected | P1 | Same key with changed body; keys scoped by user | `test_reusing_idempotency_key_with_different_payload_returns_409`, `test_idempotency_keys_are_scoped_to_authenticated_user` |
| Booking data is private to its owner | P0 | Owner access and cross-user access | `test_owner_can_read_booking_but_another_user_cannot`, `test_booking_lookup_requires_authentication` |
| Cancellation is safe and repeatable | P1 | Repeat cancellation releases slot | `test_cancel_booking_is_idempotent_and_releases_availability` |
| A user cannot cancel another user's booking | P0 | Cross-user cancellation | `test_another_user_cannot_cancel_booking` |
| Unknown resources return a controlled error | P2 | Missing booking id | `test_unknown_booking_returns_404` |

## Contract decisions

- `201 Created`: first successful booking creation.
- `200 OK` plus `Idempotency-Replayed: true`: replay of the same request/key.
- `400`: not used for request-domain validation in this sandbox; malformed or invalid input returns `422`.
- `401`: missing or unrecognized sandbox token.
- `404`: unknown resource or resource not owned by caller (privacy-safe response).
- `409`: overlapping reservation or idempotency key reused with a different payload.
- `422`: schema, date-range and capacity validation failures.

## Test data and isolation

Every test creates a new app and a new in-memory repository. No test depends on execution order or an external service. Dates are fixed to keep tests deterministic.

## Known limitations

This is a deliberately small in-memory service, not a production booking backend. It does not claim to validate a real provider's API, database transaction isolation, distributed idempotency, or production authentication. Those require a real specification and environment.
