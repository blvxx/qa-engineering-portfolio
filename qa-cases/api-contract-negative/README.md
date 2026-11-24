# Booking API — API Quality Engineering Case

<sub>Python · FastAPI · pytest · Pydantic · HTTP contract testing · coverage · GitHub Actions</sub>

![Booking API QA](https://github.com/blvxx/portfolio/actions/workflows/qa-booking-api.yml/badge.svg)

A self-contained API system and automated quality suite built around a fictional booking service. The project demonstrates how to translate API requirements into risk-based tests, isolate test state, verify contracts and protect critical booking invariants.

> **Transparency:** the API is an authored local test target. The suite proves behavior of this sandbox only; it does not claim testing of a third-party or production system.

## At a glance

| Asset | Included |
|---|---|
| Local API target | FastAPI + Pydantic, isolated in-memory repository |
| Automated suite | 31 pytest cases including parametrized boundary scenarios |
| Local execution | 31 passed; 100% statement coverage for app.py and store.py in the development run |
| CI evidence | JUnit XML and coverage XML artifacts |

## Quality objectives

| Quality risk | Test strategy |
|---|---|
| Double booking | Overlap, adjacency and state-transition tests |
| Duplicate writes on retry | Idempotency replay and key-reuse conflict |
| Unauthorized data access | Missing/invalid identity and cross-user access |
| Invalid business input | Date, capacity, email and payload-boundary validation |
| Contract drift | Response shape, status codes and headers |
| Unstable tests | Per-test app/store isolation and fixed test data |

## Verified scope in code

- Room catalogue and pagination.
- Availability and half-open date interval rules.
- Booking creation and capacity validation.
- Bearer-token authorization in a deliberately simplified sandbox.
- Owner-only read and cancellation.
- Idempotency key replay, payload mismatch and per-user key scope.
- Cancellation state and availability recovery.

## Repository map

| File | Responsibility |
|---|---|
| `app.py` | FastAPI routes, request/response contracts and HTTP semantics |
| `store.py` | Isolated in-memory repository, atomic booking and idempotency operations |
| `test_api.py` | Automated API tests using FastAPI TestClient |
| `architecture.md` | Component and test architecture, state ownership and design limitations |
| `test-matrix.md` | Risk-based requirements-to-test traceability |
| `examples.md` | Human-readable request / response examples |
| `bug-reports.md` | Hypothetical defect-report examples |

## Run locally

Python 3.10+:

```bash
cd qa-cases/api-contract-negative
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# macOS / Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
pytest
```

Run with coverage:

```bash
pytest --cov=app --cov=store --cov-report=term-missing --cov-report=xml
```

## CI evidence

GitHub Actions runs the suite on pushes and pull requests affecting this case, and can be started manually. The workflow enforces **100% statement coverage** for `app.py` and `store.py`, then publishes JUnit XML and coverage XML. The latest verified CI run completed with **31 passed**, both modules at **100%**, and the coverage gate satisfied: [GitHub Actions run](https://github.com/blvxx/portfolio/actions/runs/44993766677). [Download the JUnit + coverage artifact](https://github.com/blvxx/portfolio/actions/runs/44993705856/artifacts/14742666986).

## Test design notes

- Each test receives a fresh app instance and repository; there is no shared mutable state between tests.
- Reservation intervals use `[start_date, end_date)`: adjacent bookings are allowed, overlapping bookings are rejected.
- The idempotency key is scoped to the authenticated user. Same key + same payload replays the original booking; same key + changed payload returns conflict.
- Cross-user access intentionally returns 404 to avoid confirming the existence of another user's booking.

## Limitations

The store is in memory and not a substitute for a transactional database. The token scheme is a test fixture, not real authentication. Distributed concurrency, persistence, rate limits, observability and external integrations are intentionally out of scope.
