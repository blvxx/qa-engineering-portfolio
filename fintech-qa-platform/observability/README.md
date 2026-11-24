# FinTech Observability Lab

A local monitoring stack attached to the FinTech QA demo. Payment and Ledger expose Prometheus metrics; Prometheus scrapes both services and evaluates alert rules; Grafana loads a pre-provisioned operational dashboard.

## Start

From the fintech-qa-platform directory:

```bash
docker compose up --build -d
```

Open Grafana at http://localhost:3000 (demo credentials: admin / admin_demo_password), Prometheus at http://localhost:9090, Payment metrics at http://localhost:8000/metrics and Ledger metrics at http://localhost:8001/metrics.

The Grafana dashboard is provisioned automatically in the FinTech Demo folder. Allow 10–20 seconds for the first scrape and generate a few requests before expecting populated charts.

## Automated local fault-injection drill

With the full local Compose stack running, execute the guarded Ledger outage scenario from the project directory:

```bash
python scripts/incident_drill.py --execute-local-drill --timeout-seconds 60
```

The script validates that all configured URLs use loopback HTTP addresses, checks the baseline, stops only the local Ledger container, waits for Prometheus to observe the target as DOWN, verifies that Payment readiness remains available while a business request returns 502, restores Ledger, waits for the target to return UP and retries the same payment idempotency key. It prints a JSON evidence summary and exits non-zero if an expected state transition is missing.

The explicit flag is required because the drill stops a running container. Do not point this exercise at shared, staging or production infrastructure. It creates one small synthetic payment in the local demo database after recovery.

## Generate traffic

```bash
curl -s http://localhost:8000/health
curl -s http://localhost:8001/health
curl -s http://localhost:8000/health/ready
```

Create a successful demo payment:

```bash
curl -i -X POST http://localhost:8000/payments \
  -H 'Content-Type: application/json' \
  -d '{"idempotency_key":"monitoring-demo-001","customer_account":"customer-demo","merchant_account":"merchant-demo","amount_minor":12500,"currency":"RUB"}'
```

Generate a controlled validation error:

```bash
curl -i -X POST http://localhost:8000/payments \
  -H 'Content-Type: application/json' \
  -d '{"idempotency_key":"monitoring-demo-002","customer_account":"same-account","merchant_account":"same-account","amount_minor":100,"currency":"RUB"}'
```

## Simulate a dependency outage

Stop Ledger with docker compose stop ledger. The Prometheus Targets page should show the Ledger target as DOWN after a failed scrape. Payment readiness can remain healthy because it checks its own database connection; a payment request will fail when it calls Ledger. This distinction is useful for incident diagnosis.

Restore Ledger with docker compose start ledger. Wait for its health check and the next Prometheus scrape; the target should return to UP.

## Useful PromQL

Request rate: sum by (service) (rate(http_requests_total[5m]))

5xx rate: sum by (service) (rate(http_requests_total{status=~"5.."}[5m]))

p95 latency: histogram_quantile(0.95, sum by (le, service) (rate(http_request_duration_seconds_bucket[5m])))

Target availability: up{job=~"payment-service|ledger-service"}

Practice controlled outages and recovery checks with the [Observability Incident Drills](incident-drills.md).

## Alert rules

- FintechServiceDown: a Payment or Ledger target cannot be scraped for 30 seconds.
- ElevatedServerErrorRate: more than 5% of a service's requests return HTTP 5xx for 2 minutes (with a small denominator guard).

Prometheus evaluates these rules. Alertmanager delivery and external notifications are not configured in this first iteration.

## Metrics and cardinality

- http_requests_total: request counter labeled by service, method, route template and status code.
- http_request_duration_seconds: request duration histogram labeled by service, method and route template.
- The /metrics endpoint is excluded from its own instrumentation.
- Route templates are used instead of raw URLs to avoid high-cardinality labels such as individual payment IDs.

## Demo security notes

This is a local portfolio environment, not a production deployment. Grafana uses demo credentials, Prometheus has no authentication, and the stack must not be exposed to the public internet. No real payment or customer data is used.
