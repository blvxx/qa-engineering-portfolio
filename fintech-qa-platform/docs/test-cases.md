# Test Cases

| ID | Area | Preconditions | Steps | Expected result |
|---|---|---|---|---|
| PAY-001 | Payment API | Services available | POST a valid payment | HTTP 201; status posted; transfer ID returned |
| PAY-002 | Idempotency | PAY-001 completed | Repeat identical request/key | Existing payment returned; no second ledger call |
| PAY-003 | Idempotency | No matching payment | Reuse key with changed amount | HTTP 409; no second transfer |
| PAY-004 | Validation | API available | Submit amount_minor = 0 | HTTP 422; ledger is not called |
| PAY-005 | Validation | API available | Use same customer and merchant account | HTTP 422 |
| LED-001 | Ledger | Ledger available | Create transfer | One debit and one credit entry |
| LED-002 | Ledger | LED-001 completed | Read both balances | Debit + credit = 0 |
| LED-003 | Idempotency | Transfer exists | Repeat same key and payload | Duplicate response; balances unchanged |
| LED-004 | Idempotency | Transfer exists | Reuse key with different payload | HTTP 409 |
| INT-001 | Integration | Compose stack healthy | Create payment through Payment API | Ledger records matching transfer |
| INT-002 | Integration | INT-001 completed | Read both account balances | Customer debited; merchant credited |
| ERR-001 | Resilience | Ledger fake returns 503 | Create payment | Payment API returns HTTP 502 |
| ERR-002 | Readiness | Database reachable | GET /health/ready | HTTP 200 and database=ok |
