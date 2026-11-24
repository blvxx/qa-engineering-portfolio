# Defect Report Examples — Booking API

The following are **hypothetical defect examples** used to demonstrate report quality. They have not been observed in a production service.

## API-BUG-01 — Concurrent overlapping reservations are both accepted
- **Severity / priority:** Critical / P0
- **Component:** Booking creation
- **Preconditions:** Same room, overlapping date range, two independent clients.
- **Steps:** Submit both requests concurrently with distinct idempotency keys.
- **Expected:** At most one booking is confirmed; the other request receives 409.
- **Hypothetical actual:** Both requests return 201 and persist.
- **Evidence required:** Request timestamps, correlation IDs and persisted records.
- **Likely area:** Transaction isolation / atomic availability check.

## API-BUG-02 — Booking details disclose another customer's data
- **Severity / priority:** Critical / P0
- **Component:** Booking retrieval
- **Steps:** Authenticate as user B and request a booking owned by user A.
- **Expected:** Privacy-safe 404 and no personal data.
- **Hypothetical actual:** 200 response includes guest name/email.
- **Evidence required:** Sanitized request/response pair.
- **Likely area:** Object-level authorization.

## API-BUG-03 — Reusing an idempotency key changes the original booking
- **Severity / priority:** Major / P1
- **Component:** Booking creation / retry
- **Steps:** Create a booking with a key; retry with a different payload and the same key.
- **Expected:** 409; original booking remains unchanged.
- **Hypothetical actual:** Existing record is overwritten or second booking is created.
- **Evidence required:** Both payloads, response bodies and final stored state.
- **Likely area:** Idempotency payload fingerprinting.

## API-BUG-04 — Cancelled reservation continues blocking availability
- **Severity / priority:** Major / P1
- **Component:** Availability / cancellation
- **Steps:** Create a booking, cancel it, query availability for the same interval.
- **Expected:** Interval becomes available.
- **Hypothetical actual:** Availability still reports false.
- **Evidence required:** Booking lifecycle responses and availability response.
- **Likely area:** State filtering in availability query.

## Reporting standard

Every real defect report should include environment/build, exact request, actual response, expected response, reproducibility, impact, severity, priority and sanitized evidence. Do not report a defect until it is reproduced.
