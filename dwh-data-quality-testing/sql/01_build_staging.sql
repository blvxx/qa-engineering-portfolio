TRUNCATE TABLE staging.invoices;
INSERT INTO staging.invoices (
 batch_id, source_row, invoice_id, customer_id, invoice_date,
 amount, currency, status, source_updated_at
)
SELECT batch_id, source_row, invoice_id, customer_id, invoice_date,
 amount, UPPER(currency), LOWER(status), source_updated_at
FROM raw.invoice_events
WHERE batch_id = %(batch_id)s
ORDER BY source_row;
