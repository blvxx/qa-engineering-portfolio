# Risk Analysis

| Risk | Impact | Likelihood | Mitigation / test |
|---|---|---|---|
| Duplicate payment on retry | Critical | Medium | Idempotency tests at both service boundaries |
| Ledger mismatch | Critical | Low/Medium | Verify debit-credit conservation |
| Ledger unavailable | High | Medium | Controlled dependency failure test |
| Invalid amount accepted | High | Low | Boundary and schema validation |
| Idempotency key payload collision | High | Medium | HTTP 409 conflict scenario |
| Database unavailable | High | Medium | Readiness endpoint and Compose health checks |
| Shared database coupling | Medium | Medium | Document service table ownership; consider separate DBs in future |

## Known architectural limitation

The demo uses one PostgreSQL database instance for both services, with separate tables and service-level ownership. It does not claim distributed transaction guarantees. A production design would require an outbox/saga strategy, reconciliation and operational alerting.
