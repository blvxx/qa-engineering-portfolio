import csv
import os
import uuid
from datetime import date
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values

ROOT = Path(__file__).resolve().parents[1]
DSN = os.getenv("WAREHOUSE_DSN", "postgresql://warehouse:warehouse_demo_only@localhost:5433/warehouse")

def connect():
    return psycopg2.connect(DSN)

def execute_sql_file(cursor, relative_path, params=None):
    cursor.execute((ROOT / relative_path).read_text(encoding="utf-8"), params or {})

def create_layers():
    with connect() as conn, conn.cursor() as cur:
        execute_sql_file(cur, "sql/00_create_layers.sql")

def ingest_source(batch_id=None, from_date=None, to_date=None):
    batch_id = batch_id or str(uuid.uuid4())
    start = date.fromisoformat(from_date) if from_date else None
    end = date.fromisoformat(to_date) if to_date else None
    if start and end and start > end:
        raise ValueError("from_date must be on or before to_date")
    with (ROOT / "data/source/invoices.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if start:
        rows = [r for r in rows if date.fromisoformat(r["invoice_date"]) >= start]
    if end:
        rows = [r for r in rows if date.fromisoformat(r["invoice_date"]) <= end]
    values = [
        (batch_id, index, row["invoice_id"], row["customer_id"], row["invoice_date"],
         row["amount"], row["currency"], row["status"], row["source_updated_at"])
        for index, row in enumerate(rows, start=1)
    ]
    with connect() as conn, conn.cursor() as cur:
        # Re-running the same Airflow batch replaces that batch, not appends duplicates.
        cur.execute("DELETE FROM raw.invoice_events WHERE batch_id = %s::uuid", (batch_id,))
        if values:
            execute_values(
                cur,
                """INSERT INTO raw.invoice_events
                (batch_id, source_row, invoice_id, customer_id, invoice_date, amount, currency, status, source_updated_at)
                VALUES %s""",
                values,
            )
    return batch_id, len(rows)

def build_staging(batch_id):
    with connect() as conn, conn.cursor() as cur:
        execute_sql_file(cur, "sql/01_build_staging.sql", {"batch_id": batch_id})

def _record_checks(cur, checks):
    run_id = str(uuid.uuid4())
    for rule, passed, observed, expected, details in checks:
        cur.execute(
            """INSERT INTO dq.results
            (run_id, rule_id, status, observed_value, expected_value, details)
            VALUES (%s, %s, %s, %s, %s, %s)""",
            (run_id, rule, "PASS" if passed else "FAIL", str(observed), str(expected), details),
        )
    return run_id

def staging_quality_gate(batch_id):
    with connect() as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM raw.invoice_events WHERE batch_id = %s::uuid", (batch_id,))
        raw_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM staging.invoices WHERE batch_id = %s::uuid", (batch_id,))
        stage_count = cur.fetchone()[0]
        cur.execute("""SELECT COUNT(*) FROM (
            SELECT invoice_id FROM staging.invoices GROUP BY invoice_id HAVING COUNT(*) > 1
        ) d""")
        duplicates = cur.fetchone()[0]
        cur.execute("""SELECT COUNT(*) FROM staging.invoices
            WHERE NULLIF(TRIM(invoice_id), '') IS NULL
               OR NULLIF(TRIM(customer_id), '') IS NULL
               OR invoice_date IS NULL OR amount IS NULL OR amount <= 0
               OR currency NOT IN ('RUB', 'EUR', 'USD')
               OR status NOT IN ('paid', 'unpaid', 'overdue')""")
        invalid_rows = cur.fetchone()[0]
        checks = [
            ("DQ-001", raw_count == stage_count, raw_count, stage_count, "Raw-to-staging row count"),
            ("DQ-002", duplicates == 0, duplicates, 0, "Staging key uniqueness"),
            ("DQ-003/004/005", invalid_rows == 0, invalid_rows, 0, "Required fields, amount and domain values"),
        ]
        run_id = _record_checks(cur, checks)
    failures = [item for item in checks if not item[1]]
    if failures:
        raise RuntimeError(f"Pre-promotion DQ gate failed: {failures}")
    return {"run_id": run_id, "checks": len(checks), "status": "PASS"}

def build_core():
    with connect() as conn, conn.cursor() as cur:
        execute_sql_file(cur, "sql/02_build_core.sql")

def build_mart():
    with connect() as conn, conn.cursor() as cur:
        execute_sql_file(cur, "sql/03_build_mart.sql")

def quality_gate(batch_id):
    with connect() as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM raw.invoice_events WHERE batch_id = %s::uuid", (batch_id,))
        source_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM staging.invoices WHERE batch_id = %s::uuid", (batch_id,))
        staging_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM (SELECT invoice_id FROM core.invoices GROUP BY invoice_id HAVING COUNT(*) > 1) d")
        duplicates = cur.fetchone()[0]
        cur.execute("SELECT COALESCE(SUM(amount_total), 0) FROM mart.daily_invoice_summary")
        mart_total = cur.fetchone()[0]
        cur.execute("SELECT COALESCE(SUM(amount), 0) FROM core.invoices")
        core_total = cur.fetchone()[0]
        cur.execute("SELECT COALESCE(SUM(invoice_count), 0) FROM mart.daily_invoice_summary")
        mart_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM core.invoices")
        core_count = cur.fetchone()[0]
        checks = [
            ("DQ-001", source_count == staging_count, source_count, staging_count, "Raw-to-staging count"),
            ("DQ-006", duplicates == 0, duplicates, 0, "Core key uniqueness"),
            ("DQ-007-amount", mart_total == core_total, mart_total, core_total, "Mart-to-core amount reconciliation"),
            ("DQ-007-count", mart_count == core_count, mart_count, core_count, "Mart-to-core count reconciliation"),
        ]
        run_id = _record_checks(cur, checks)
    failures = [item for item in checks if not item[1]]
    if failures:
        raise RuntimeError(f"Final DWH quality gate failed: {failures}")
    return {"run_id": run_id, "checks": len(checks), "status": "PASS"}

def run_pipeline():
    create_layers()
    batch_id, source_count = ingest_source()
    build_staging(batch_id)
    staging_quality_gate(batch_id)
    build_core()
    build_mart()
    return {"batch_id": batch_id, "source_rows": source_count, **quality_gate(batch_id)}

if __name__ == "__main__":
    print(run_pipeline())
