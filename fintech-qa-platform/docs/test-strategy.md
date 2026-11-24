# Test Strategy

## Objective

Validate the correctness and resilience of a demonstration payment flow spanning Payment Service, Ledger Service and PostgreSQL.

## Quality risks

1. A payment is marked as posted although the ledger transfer failed.
2. Retried requests create duplicate ledger entries.
3. Reusing an idempotency key with a different payload is accepted.
4. Debit and credit entries do not balance.
5. Invalid amounts or identical source/destination accounts are accepted.
6. A service reports readiness while its database is unavailable.

## Test levels

- Unit: validation and service-level business rules.
- API: HTTP status, response contract, input validation and error mapping.
- Integration: Payment Service to Ledger Service interaction.
- End-to-end: payment creation followed by account balance verification in Docker Compose.
- Data: SQL-level balance and transfer consistency checks.

## Test approach

Use deterministic SQLite databases for fast automated tests and PostgreSQL in the Docker Compose smoke flow. External services are not required. The Payment Service's Ledger dependency is replaced with a controlled fake in isolated API tests.

## Entry criteria

- Dependencies install successfully.
- Both service applications import.
- Test database can be created.

## Exit criteria

- All unit/API tests pass.
- Ruff reports no lint errors.
- Docker Compose smoke flow creates one payment and verifies both ledger balances.
- CI artifacts include JUnit test results.

## Test data

All account identifiers and transactions are synthetic. Amounts are represented in minor currency units (for RUB, kopecks).
