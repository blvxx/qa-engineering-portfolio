# Source-to-target mapping

## Source contract

File: data/source/invoices.csv

| Source field | Type | Required | Target field | Transformation |
|---|---|---:|---|---|
| invoice_id | string | Yes | raw/staging/core.invoice_id | Preserve source key |
| customer_id | string | Yes | raw/staging/core.customer_id | Trim |
| invoice_date | ISO date | Yes | raw/staging/core.invoice_date | Parse as DATE |
| amount | decimal | Yes | raw/staging/core.amount | NUMERIC(18,2); must be > 0 |
| currency | string | Yes | raw/staging/core.currency | Uppercase; allow-list RUB/EUR/USD |
| status | string | Yes | raw/staging/core.status | Lowercase; allow-list paid/unpaid/overdue |
| source_updated_at | ISO datetime | Yes | raw/staging/core.source_updated_at | Parse with timezone |

## Layer semantics

- **Raw:** source-preserving event batch; batch ID and source row are lineage metadata.
- **Staging:** type-normalised and domain-normalised records for a selected batch. Rows remain visible so duplicate source keys can be detected.
- **Core:** one current record per invoice ID. After the pre-promotion DQ gate passes, current source rows are upserted by key.
- **Mart:** daily invoice count and amount by currency and status.
- **DQ:** one result row per rule and execution run.

## Reconciliation invariants

1. Raw batch count = staging batch count.
2. Staging duplicate invoice key count = 0 for a passing run.
3. Required fields are non-null/non-blank.
4. Amount > 0; domain values are allow-listed.
5. Core invoice key is unique.
6. Sum of mart amount totals = sum of core invoice amounts.
7. Sum of mart invoice counts = core invoice count.
8. Re-running the same logical Airflow run reuses a deterministic batch ID and must not append duplicates.

This demo uses an upsert for the current-state entity. A production CDC design would also need tombstones, late-arriving-event rules, partitioning and source watermarks.
