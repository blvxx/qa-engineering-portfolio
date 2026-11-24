TRUNCATE TABLE mart.daily_invoice_summary;
INSERT INTO mart.daily_invoice_summary (
 invoice_date, currency, status, invoice_count, amount_total, refreshed_at
)
SELECT invoice_date, currency, status, COUNT(*), SUM(amount), NOW()
FROM core.invoices
GROUP BY invoice_date, currency, status;
