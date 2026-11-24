-- Synthetic-data quality checks for the FinTech QA Engineering Platform.
-- Run against the PostgreSQL database used by docker-compose.

-- 1. Find transfers whose ledger entries do not net to zero.
SELECT
    t.id AS transfer_id,
    t.idempotency_key,
    COALESCE(SUM(e.amount_minor), 0) AS net_amount_minor,
    COUNT(e.id) AS entry_count
FROM ledger_transfers AS t
LEFT JOIN ledger_entries AS e ON e.transfer_id = t.id
GROUP BY t.id, t.idempotency_key
HAVING COUNT(e.id) <> 2 OR COALESCE(SUM(e.amount_minor), 0) <> 0;

-- 2. Find payments that have no corresponding ledger transfer.
SELECT
    p.id AS payment_id,
    p.idempotency_key,
    p.status,
    p.ledger_transfer_id
FROM qa_payments AS p
LEFT JOIN ledger_transfers AS t
    ON t.id = p.ledger_transfer_id
WHERE p.status = 'posted'
  AND t.id IS NULL;

-- 3. Find payment/ledger amount or currency mismatches.
SELECT
    p.id AS payment_id,
    p.idempotency_key,
    p.amount_minor AS payment_amount_minor,
    t.amount_minor AS ledger_amount_minor,
    p.currency AS payment_currency,
    t.currency AS ledger_currency
FROM qa_payments AS p
JOIN ledger_transfers AS t
    ON t.id = p.ledger_transfer_id
WHERE p.status = 'posted'
  AND (
      p.amount_minor <> t.amount_minor
      OR p.currency <> t.currency
  );

-- 4. Reconcile balances from the immutable ledger entries.
SELECT
    account_id,
    currency,
    SUM(amount_minor) AS balance_minor
FROM ledger_entries
GROUP BY account_id, currency
ORDER BY account_id, currency;
