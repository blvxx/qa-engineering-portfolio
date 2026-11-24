-- Upsert current records after the staging DQ gate passes.
-- Partial date-slice replays must not delete entities outside the selected range.
INSERT INTO core.invoices (
 invoice_id, customer_id, invoice_date, amount, currency, status, source_updated_at, loaded_at
)
SELECT DISTINCT ON (invoice_id)
 invoice_id, customer_id, invoice_date, amount, currency, status, source_updated_at, NOW()
FROM staging.invoices
ORDER BY invoice_id, source_updated_at DESC, source_row DESC
ON CONFLICT (invoice_id) DO UPDATE SET
 customer_id = EXCLUDED.customer_id,
 invoice_date = EXCLUDED.invoice_date,
 amount = EXCLUDED.amount,
 currency = EXCLUDED.currency,
 status = EXCLUDED.status,
 source_updated_at = EXCLUDED.source_updated_at,
 loaded_at = NOW();
