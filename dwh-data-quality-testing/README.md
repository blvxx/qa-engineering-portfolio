# DWH Data Quality & ETL Testing Platform

[![DWH Data Quality CI](https://github.com/blvxx/qa-engineering-portfolio/actions/workflows/dwh-quality.yml/badge.svg)](https://github.com/blvxx/qa-engineering-portfolio/actions/workflows/dwh-quality.yml)

> Independent portfolio lab using synthetic invoice data. Not a production bank/DWH implementation and not prior commercial Airflow or Cube experience.

**Target roles:** QA Engineer · Data QA · ETL QA · Integration QA · Python QA Automation

A reproducible mini data warehouse demonstrating layered modelling, Airflow orchestration, SQL/Python checks and source-to-target reconciliation.

## Architecture

~~~mermaid
flowchart LR
 A[CSV Source] --> B[Raw] --> C[Staging] --> D[Core] --> E[Data Mart]
 F[Airflow DAG] -. orchestrates .-> B
 F -.-> C
 F -.-> D
 F -.-> E
 F --> G[Quality Gates]
~~~

- Raw: source batches with batch and row lineage.
- Staging: typed, normalised records.
- Core: current invoice entities.
- Mart: daily aggregates by currency and status.
- DQ: row counts, uniqueness, required fields, domain values and aggregate reconciliation.

## Implemented

- PostgreSQL raw/staging/core/mart/DQ schemas.
- Python ingestion and SQL transformations.
- Airflow DAG with pre-promotion validation, retries and a final reconciliation gate.
- Deterministic batch ID for safe task retry/replay.
- Unit tests for duplicate keys, missing fields, invalid amounts and domain values.
- GitHub Actions workflow against PostgreSQL.
- Synthetic source data and documented negative cases.

Cube REST API and dbt are extension points documented separately, not deployed components in this release.

## Run locally

Requirements: Docker Engine/Desktop and Docker Compose v2.

~~~bash
docker compose up -d warehouse
docker compose run --rm pipeline
~~~

Start Airflow:

~~~bash
docker compose up -d airflow
~~~

Open http://127.0.0.1:8080. Airflow standalone prints its generated local admin password in startup logs. Trigger DAG **dwh_data_quality_pipeline**. For a date-slice replay, provide from_date and to_date in DAG run configuration as ISO dates (YYYY-MM-DD). Do not expose this demo stack publicly.

Run unit tests:

~~~bash
python -m venv .venv
pip install -r requirements.txt
PYTHONPATH=src pytest -q
~~~

## Quality rules

| Rule | Check | Expected |
|---|---|---|
| DQ-001 | Raw/staging row counts | Equal for selected batch |
| DQ-002 | Staging invoice-key uniqueness | Duplicates block core promotion |
| DQ-003 | Required identifiers/dates | No NULL/blank required values |
| DQ-004 | Amount | Greater than zero |
| DQ-005 | Currency/status | Allow-listed values |
| DQ-006 | Core uniqueness | One row per invoice ID |
| DQ-007 | Mart/core reconciliation | Counts and totals match |
| DQ-008 | Idempotency | Reprocessing does not duplicate core keys |

See [test scenarios](docs/test-scenarios.md), [source-to-target mapping](docs/source-to-target.md), [Airflow recovery notes](docs/airflow-recovery.md) and [Cube extension design](docs/olap-cube-extension.md).


## Verified CI evidence

[Successful DWH Data Quality CI run — 24 November 2026](https://github.com/blvxx/qa-engineering-portfolio/actions/runs/45413753188). The workflow successfully compiled the source and DAG, ran the PostgreSQL pipeline and quality gates, and completed the Python unit tests.

## Limitations

Synthetic data only; one PostgreSQL instance represents logical DWH layers; teaching-scale batch, not an MPP benchmark. The date-slice replay demonstrates orchestration parameters, not a production CDC strategy. Cube and dbt are design-only future extensions. Demo credentials must never be reused in production.


The PostgreSQL integration and unit-test workflow is defined in [.github/workflows/dwh-quality.yml](../.github/workflows/dwh-quality.yml).
