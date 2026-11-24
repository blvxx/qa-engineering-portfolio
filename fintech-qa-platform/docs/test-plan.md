# FinTech QA Platform — Test Plan and Strategy

## 1. Purpose and system under test

This document describes how the fictional payment product is validated, the risks covered by the current automated checks and the guarantees outside the demo scope.

The system contains a Payment Service, a Ledger Service, PostgreSQL persistence, an Nginx-routed UI and browser-level payment flows. It uses synthetic data only; no real money, bank integrations or customer records are involved.

## 2. Critical business invariants

1. A valid payment creates the expected debit and credit ledger entries.
2. The ledger remains balanced.
3. Repeating a request with the same idempotency key does not post the ledger operation twice.
4. Reusing an idempotency key with a conflicting payload is rejected.
5. Invalid payment data does not mutate the ledger.
6. Dependency failures are surfaced and diagnosable through service behavior and telemetry.

## 3. Test layers and evidence

| Layer | Purpose | Current repository evidence |
|---|---|---|
| Unit / API | Request validation, business rules, response codes and deterministic behavior | pytest API and service tests |
| Contract / integration | Payment-to-Ledger interaction, idempotency and database-backed behavior | Docker Compose integration smoke test |
| Browser E2E | Submit a payment through the UI and verify the resulting balance | Playwright scenarios |
| Operational / fault injection | Observe a controlled Ledger outage, 502 behavior, recovery and idempotent retry | Guarded local incident drill |
| Manual exploratory | Explore usability and edge conditions outside scripted coverage | Suggested charter below; not presented as executed testing |

## 4. Risk-based coverage matrix

| Risk | Expected behavior | Validation layer |
|---|---|---|
| Invalid or non-positive amount | Reject request; no ledger posting | Unit / API |
| Same source and destination account | Reject request | Unit / API |
| Duplicate request with same idempotency key | Do not post a second transfer | Unit / API, integration |
| Same key with changed payload | Return conflict | Unit / API |
| Ledger unavailable | Surface a dependency failure and preserve diagnosable state | Integration, local fault drill |
| Payment succeeds | UI shows success and account balance reflects the ledger result | Browser E2E |
| Database unavailable at readiness check | Readiness reports unavailable | API / integration |
| Browser validation error | Invalid value is blocked and feedback is visible | Browser E2E |

This matrix maps important risks to the current intended checks. It is not a claim that every possible permutation or failure mode has been exhaustively tested. Use the test code and latest CI run to confirm the exact current execution results.

## 5. Test data, isolation and safety

- Use synthetic customer and merchant accounts only.
- Keep tests independent; do not rely on execution order.
- Use unique idempotency keys for scenarios that create payments.
- Never commit real payment credentials, customer information or production tokens.
- Local API tests and Docker Compose integration checks use different persistence paths; passing one layer does not replace the other.

## 6. Local verification

From the `fintech-qa-platform` directory:

```bash
python -m venv .venv
python -m pip install -r requirements.txt
python -m playwright install chromium

# API and service tests
pytest tests

# Static checks
ruff check services tests e2e
```

Start the local services before browser E2E and the explicit fault-injection drill:

```bash
docker compose up --build -d
pytest e2e --alluredir=allure-results
python scripts/incident_drill.py --execute-local-drill --timeout-seconds 60
```

The incident drill intentionally stops the local Ledger container. Run it only against the loopback-bound demo environment. Do not point it at shared, staging or production systems.

## 7. CI quality gates and reporting

GitHub Actions runs static checks, API tests, a Docker Compose integration smoke test and browser E2E checks. The workflow publishes JUnit and Allure evidence as artifacts.

For each failure, classify whether it is:
- product behavior;
- test data or fixture setup;
- environment or dependency;
- test instability or timing.

Inspect the failing step and evidence before retrying. A workflow definition or status badge alone is not proof that an individual scenario passed.

## 8. Explicit non-goals

This project does not claim:
- real payment processing or bank/acquirer integration;
- production-grade authentication, authorization or fraud controls;
- PCI DSS certification or a security audit;
- distributed transaction guarantees between production systems;
- formal performance or load-test results;
- exhaustive resilience testing for every database/network failure.

These are separate engineering and assurance activities, not implied by passing the current demo test suite.

## 9. Suggested exploratory charter

Record actual execution results separately; do not mark these items executed until evidence has been captured.

1. Submit a valid payment and inspect the resulting balance.
2. Repeat the same request with the same idempotency key.
3. Reuse the key while changing the amount.
4. Try zero, negative, malformed and excessively large values.
5. Stop Ledger locally, submit a payment, inspect the HTTP response and service logs, then restore Ledger.
6. Retry using the original idempotency key and verify that no duplicate ledger posting occurred.

## 10. Review checklist

- [ ] Business invariant has at least one linked automated scenario.
- [ ] Negative paths assert both response behavior and absence of incorrect side effects where relevant.
- [ ] Integration tests run against the service boundary, not only mocks.
- [ ] Browser checks verify a user-visible outcome, not only element presence.
- [ ] Failure-injection steps are explicitly guarded and target local resources only.
- [ ] Reports retain enough context to reproduce and diagnose failures.
