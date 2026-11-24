# Observability Incident Drills

These drills use the local synthetic FinTech environment. Run them only on the local Docker Compose stack; do not expose the demo services or dashboards to the public internet.

## Start the environment

From `fintech-qa-platform/`:

```bash
docker compose up --build -d
docker compose ps
```

Open Prometheus at http://localhost:9090 and Grafana at http://localhost:3000. Demo credentials are documented in the project README. Wait for at least two scrape intervals before interpreting target state.

## Drill 1 — Ledger dependency outage

**Objective:** distinguish service availability from end-to-end payment capability.

1. Confirm Payment and Ledger targets are UP in Prometheus.
2. Stop only Ledger: `docker compose stop ledger`.
3. Inspect the target and query `up{job="ledger-service"}`.
4. Trigger a demo payment request using the example from `observability/README.md`.
5. Inspect logs with `docker compose logs --since=5m payment ledger`.

**Expected observations:**
- The Ledger scrape target transitions to DOWN after a failed scrape.
- Payment may answer its own health endpoint while business requests depending on Ledger fail.
- The `FintechServiceDown` alert condition becomes true after its configured `for` period.

Restore Ledger with `docker compose start ledger`. Wait for its health check and target state to return UP. Repeat a business request with a new idempotency key and verify the expected balance effect.

## Drill 2 — Elevated 5xx rate

**Objective:** distinguish actual server errors from validation responses and target health.

1. Generate valid demo requests and record the baseline.
2. Submit the documented invalid same-account payment payload.
3. Query:

```promql
sum by (service) (rate(http_requests_total{status=~"5.."}[5m]))
/
clamp_min(sum by (service) (rate(http_requests_total[5m])), 0.001)
```

4. Check whether generated failures are HTTP 5xx. Validation responses such as 4xx must not trigger this alert.
5. For a controlled 5xx exercise, stop Ledger and send requests through Payment; confirm actual response codes before interpreting the alert.

A small sample or 4xx-only traffic is not evidence of a 5xx incident. Alert evaluation depends on the actual status labels and the configured two-minute window.

## Drill 3 — Recovery verification and handover

After restoring a dependency:
- Confirm container health and Prometheus target state.
- Make a representative read and write request.
- Check that error and latency rates move back toward baseline.
- Verify no duplicate ledger effect was created during retries.
- Record detection time, mitigation time and recovery evidence in the [incident report template](../../support-engineering-lab/docs/incident-report-template.md).

## What to include in the portfolio report

- Timestamped screenshots of Prometheus targets and Grafana panels.
- Exact PromQL queries and alert expressions.
- Before / during / after observations.
- Commands and HTTP status codes.
- A clear statement that this is a controlled local simulation.


## Drill 4 — Automated local fault injection

**Objective:** collect repeatable evidence for a dependency outage, a controlled 502 and recovery through an idempotent retry.

1. Start the full local stack and confirm the baseline health checks and Prometheus targets are UP.
2. From the project root, run:

```bash
python scripts/incident_drill.py --execute-local-drill --timeout-seconds 60
```

3. Review the JSON output.

**Expected evidence:**
- Payment and Ledger are ready before the drill.
- Prometheus observes the Ledger target transition to DOWN.
- Payment readiness remains HTTP 200 while a business request that depends on Ledger returns HTTP 502.
- The script restores the Ledger container and waits for readiness and a Prometheus UP state.
- Retrying the same idempotency key posts the payment successfully and returns the duplicate/retry indicator.

The script rejects non-loopback URLs and does not run without the explicit `--execute-local-drill` flag. It stops only the Compose service named `ledger` in this project. It is a local simulation and must never be used against shared or production systems.
