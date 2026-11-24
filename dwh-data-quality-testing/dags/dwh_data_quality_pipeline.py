import sys
import uuid
from datetime import datetime, timedelta

sys.path.insert(0, "/opt/airflow/src")

from airflow import DAG
from airflow.operators.python import PythonOperator
from pipeline import (
    build_core, build_mart, build_staging, create_layers,
    ingest_source, quality_gate, staging_quality_gate,
)

DEFAULT_ARGS = {"owner": "portfolio", "retries": 2, "retry_delay": timedelta(minutes=1)}

def _ingest(**context):
    dag_run = context.get("dag_run")
    conf = (dag_run.conf or {}) if dag_run else {}
    batch_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"dwh:{dag_run.run_id}"))
    batch_id, row_count = ingest_source(
        batch_id=batch_id,
        from_date=conf.get("from_date"),
        to_date=conf.get("to_date"),
    )
    context["ti"].xcom_push(key="batch_id", value=batch_id)
    context["ti"].xcom_push(key="source_rows", value=row_count)

def _stage(**context):
    batch_id = context["ti"].xcom_pull(task_ids="ingest_source", key="batch_id")
    build_staging(batch_id)

def _pre_gate(**context):
    batch_id = context["ti"].xcom_pull(task_ids="ingest_source", key="batch_id")
    return staging_quality_gate(batch_id)

def _final_gate(**context):
    batch_id = context["ti"].xcom_pull(task_ids="ingest_source", key="batch_id")
    return quality_gate(batch_id)

with DAG(
    dag_id="dwh_data_quality_pipeline",
    description="Synthetic DWH: raw -> staging -> validated core -> mart -> DQ gate",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    tags=["portfolio", "dwh", "data-quality"],
) as dag:
    prepare = PythonOperator(task_id="create_layers", python_callable=create_layers)
    ingest = PythonOperator(task_id="ingest_source", python_callable=_ingest)
    staging = PythonOperator(task_id="build_staging", python_callable=_stage)
    pre_gate = PythonOperator(task_id="staging_quality_gate", python_callable=_pre_gate)
    core = PythonOperator(task_id="build_core", python_callable=build_core)
    mart = PythonOperator(task_id="build_mart", python_callable=build_mart)
    final_gate = PythonOperator(task_id="final_quality_gate", python_callable=_final_gate)
    prepare >> ingest >> staging >> pre_gate >> core >> mart >> final_gate
