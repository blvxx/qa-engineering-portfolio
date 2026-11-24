# Airflow retry, replay and date-slice behavior

## DAG structure

create_layers → ingest_source → build_staging → staging_quality_gate → build_core → build_mart → final_quality_gate

The pre-promotion DQ gate is intentional: invalid staging records must not be merged into core. The final gate checks core/mart consistency after transformation.

## Retry safety

- Airflow task retries are configured to 2 with a one-minute retry delay.
- The ingestion task derives a deterministic UUID from the Airflow DAG run ID.
- Before inserting, ingestion deletes rows for that same batch ID and reloads the same source slice.
- Core uses a stable invoice primary key and upsert semantics.
- Mart is rebuilt from core rather than incrementally adding to previous totals.

This is a teaching-scale idempotency pattern. It does not replace transaction design, source watermarks or event deduplication for a production CDC stream.

## Date-slice replay

Set DAG run configuration:

~~~json
{
  "from_date": "2026-11-01",
  "to_date": "2026-11-05"
}
~~~

The pipeline filters the synthetic source by inclusive invoice_date boundaries. It demonstrates a controlled date-slice rerun, not continuous scheduled historical catchup. The core step is an upsert; it does not delete entities absent from a partial date slice.

## Recovery checks

1. Inspect Airflow task log and exception.
2. Confirm the failing rule or connection.
3. Correct only the relevant issue.
4. Retry/clear the task.
5. Verify the same batch ID is used for the same DAG run.
6. Confirm core key count and mart totals.
7. Review DQ result records for the run.
