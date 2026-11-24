from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}


def validate_local_url(value: str) -> None:
    parsed = urlsplit(value)
    if parsed.scheme != "http" or parsed.hostname not in LOCAL_HOSTS:
        raise ValueError("The drill only accepts http://localhost or loopback URLs.")


def parse_prometheus_target(payload: dict, job_name: str = "ledger-service") -> bool | None:
    """Return True/False for the selected Prometheus target; None if absent."""
    results = payload.get("data", {}).get("result", [])
    for item in results:
        if item.get("metric", {}).get("job") == job_name:
            try:
                return float(item["value"][1]) == 1.0
            except (KeyError, IndexError, TypeError, ValueError):
                return None
    return None


def request_json(url: str, method: str = "GET", payload: dict | None = None, timeout: float = 4.0) -> tuple[int | None, dict | str]:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    request = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
            try:
                return response.status, json.loads(raw) if raw else {}
            except json.JSONDecodeError:
                return response.status, raw[:500]
    except HTTPError as error:
        raw = error.read().decode("utf-8", errors="replace")
        try:
            body = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            body = raw[:500]
        return error.code, body
    except (URLError, TimeoutError, OSError) as error:
        return None, str(error)


def query_ledger_target(prometheus_url: str) -> bool | None:
    query = urlencode({"query": 'up{job="ledger-service"}'})
    status_code, body = request_json(prometheus_url.rstrip("/") + "/api/v1/query?" + query)
    if status_code != 200 or not isinstance(body, dict):
        return None
    return parse_prometheus_target(body)


def wait_until(check: Callable[[], bool], timeout_seconds: int, interval_seconds: float = 2.0) -> bool:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if check():
            return True
        time.sleep(interval_seconds)
    return check()


def compose(project_root: Path, action: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["docker", "compose", action, "ledger"],
        cwd=project_root,
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )


def run_drill(
    payment_url: str,
    ledger_url: str,
    prometheus_url: str,
    timeout_seconds: int,
) -> dict:
    for value in (payment_url, ledger_url, prometheus_url):
        validate_local_url(value)
    if timeout_seconds < 10:
        raise ValueError("Use a timeout of at least 10 seconds so Prometheus can complete a scrape.")

    services = subprocess.run(
        ["docker", "compose", "config", "--services"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    ).stdout.split()
    if not {"payment", "ledger", "prometheus"}.issubset(set(services)):
        raise RuntimeError("Expected payment, ledger and prometheus services in this Compose project.")

    def baseline_is_ready() -> bool:
        payment_status = request_json(payment_url.rstrip("/") + "/health/ready")[0]
        ledger_status = request_json(ledger_url.rstrip("/") + "/health/ready")[0]
        target_status = query_ledger_target(prometheus_url)
        return payment_status == 200 and ledger_status == 200 and target_status is True

    if not wait_until(baseline_is_ready, timeout_seconds):
        raise RuntimeError(
            "Baseline check failed: Payment, Ledger and the Prometheus Ledger target "
            "must all be ready before fault injection."
        )

    payment_ready = request_json(payment_url.rstrip("/") + "/health/ready")
    ledger_ready = request_json(ledger_url.rstrip("/") + "/health/ready")
    target_before = query_ledger_target(prometheus_url)

    idempotency_key = "ops-drill-" + uuid.uuid4().hex[:24]
    payment_payload = {
        "idempotency_key": idempotency_key,
        "customer_account": "ops-drill-customer",
        "merchant_account": "ops-drill-merchant",
        "amount_minor": 100,
        "currency": "RUB",
    }
    report = {
        "scenario": "ledger_dependency_outage_and_recovery",
        "environment": "local_docker_compose_only",
        "started_at_epoch": int(time.time()),
        "baseline_payment_ready": payment_ready[0] == 200,
        "baseline_ledger_ready": ledger_ready[0] == 200,
        "ledger_target_before": target_before,
        "idempotency_key": idempotency_key,
    }
    stopped = False
    try:
        compose(PROJECT_ROOT, "stop")
        stopped = True
        report["ledger_target_down_confirmed"] = wait_until(
            lambda: query_ledger_target(prometheus_url) is False,
            timeout_seconds,
        )
        during_payment_ready = request_json(payment_url.rstrip("/") + "/health/ready")
        report["payment_readiness_during_outage"] = during_payment_ready[0]
        outage_status, outage_body = request_json(
            payment_url.rstrip("/") + "/payments",
            method="POST",
            payload=payment_payload,
            timeout=8.0,
        )
        report["payment_request_during_outage_status"] = outage_status
        report["payment_request_during_outage_body"] = outage_body
    finally:
        if stopped:
            compose(PROJECT_ROOT, "start")

    report["ledger_ready_after_restore"] = wait_until(
        lambda: request_json(ledger_url.rstrip("/") + "/health/ready")[0] == 200,
        timeout_seconds,
    )
    report["ledger_target_up_after_restore"] = wait_until(
        lambda: query_ledger_target(prometheus_url) is True,
        timeout_seconds,
    )
    retry_status, retry_body = request_json(
        payment_url.rstrip("/") + "/payments",
        method="POST",
        payload=payment_payload,
        timeout=8.0,
    )
    report["recovery_retry_status"] = retry_status
    report["recovery_retry_body"] = retry_body
    report["finished_at_epoch"] = int(time.time())
    report["passed"] = (
        report["ledger_target_down_confirmed"]
        and report["payment_readiness_during_outage"] == 200
        and report["payment_request_during_outage_status"] == 502
        and report["ledger_ready_after_restore"]
        and report["ledger_target_up_after_restore"]
        and retry_status == 201
        and isinstance(retry_body, dict)
        and retry_body.get("status") == "posted"
        and retry_body.get("duplicate") is True
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Stop the local Ledger container, observe a controlled 502, restore it and retry safely."
    )
    parser.add_argument("--execute-local-drill", action="store_true", help="Required explicit confirmation to stop the local Ledger container.")
    parser.add_argument("--payment-url", default="http://localhost:8000")
    parser.add_argument("--ledger-url", default="http://localhost:8001")
    parser.add_argument("--prometheus-url", default="http://localhost:9090")
    parser.add_argument("--timeout-seconds", type=int, default=60)
    args = parser.parse_args()

    if not args.execute_local_drill:
        parser.error("No action taken. Add --execute-local-drill to confirm this local fault-injection exercise.")

    try:
        report = run_drill(
            args.payment_url,
            args.ledger_url,
            args.prometheus_url,
            args.timeout_seconds,
        )
    except Exception as error:  # surface setup, Docker and recovery errors clearly
        print(json.dumps({"passed": False, "error": str(error)}, ensure_ascii=False, indent=2))
        return 1

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
