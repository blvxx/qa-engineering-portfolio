CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS mart;
CREATE SCHEMA IF NOT EXISTS dq;

CREATE TABLE IF NOT EXISTS raw.invoice_events (
 batch_id UUID NOT NULL, source_row INTEGER NOT NULL, invoice_id TEXT,
 customer_id TEXT, invoice_date DATE, amount NUMERIC(18,2), currency TEXT,
 status TEXT, source_updated_at TIMESTAMPTZ
);
CREATE TABLE IF NOT EXISTS staging.invoices (
 batch_id UUID NOT NULL, source_row INTEGER NOT NULL, invoice_id TEXT,
 customer_id TEXT, invoice_date DATE, amount NUMERIC(18,2), currency TEXT,
 status TEXT, source_updated_at TIMESTAMPTZ
);
CREATE TABLE IF NOT EXISTS core.invoices (
 invoice_id TEXT PRIMARY KEY, customer_id TEXT NOT NULL, invoice_date DATE NOT NULL,
 amount NUMERIC(18,2) NOT NULL, currency TEXT NOT NULL, status TEXT NOT NULL,
 source_updated_at TIMESTAMPTZ NOT NULL, loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS mart.daily_invoice_summary (
 invoice_date DATE NOT NULL, currency TEXT NOT NULL, status TEXT NOT NULL,
 invoice_count BIGINT NOT NULL, amount_total NUMERIC(20,2) NOT NULL,
 refreshed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
 PRIMARY KEY (invoice_date, currency, status)
);
CREATE TABLE IF NOT EXISTS dq.results (
 run_id UUID NOT NULL, rule_id TEXT NOT NULL, status TEXT NOT NULL,
 observed_value TEXT, expected_value TEXT, details TEXT,
 checked_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
