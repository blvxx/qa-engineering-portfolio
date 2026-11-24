# Postman

Import fintech-qa-platform.postman_collection.json.

Set collection variables:
- paymentUrl: http://localhost:8000
- ledgerUrl: http://localhost:8001
- idempotencyKey: postman-demo-0001
- paymentId: 1

Run requests in this order:
1. Create payment
2. Get payment
3. Customer balance
4. Merchant balance
5. Repeat payment (idempotency)

The collection uses synthetic account identifiers and minor currency units.
