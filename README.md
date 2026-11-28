# QA Engineering — Project Evidence & Test Labs

> **Portfolio navigation:** use the [single career portfolio](https://blvxx.github.io/portfolio/) for the employer-facing overview. This repository contains supporting QA evidence: test projects, automation code, test strategies, reports and CI workflows.


**Web/API Testing · Python Automation · Integration & Data Quality**

I build reproducible QA case studies around functional, regression, exploratory, API and integration testing. The portfolio combines test design with Python, pytest, Playwright, SQL and Docker-based environments. Its focus is risk-based coverage, reliable user journeys, data integrity, defect investigation and evidence-based release decisions.

**Target roles:** QA Engineer · Manual QA Engineer · API Tester · QA Automation Engineer (Python) · Integration QA · Data QA

**Mobile scope note:** the repository includes mobile/Android TV test-design checklists and scenario libraries. These documents demonstrate test-design knowledge; they are not presented as evidence of a completed physical-device compatibility matrix.

[GitHub profile](https://github.com/blvxx) · [Email](mailto:blvx8x@gmail.com) · [Telegram](https://t.me/blvlxx)

## Core QA capabilities

- **Web testing:** functional and regression testing, responsive behavior, Chrome DevTools (Elements, Console, Network, Application, Device Toolbar).
- **Mobile test design:** Android/iOS lifecycle, permissions, connectivity, sessions and error-handling scenarios documented as reusable checklists.
- **TV test design:** Android TV / Smart TV installation, D-pad navigation, visible focus, remote-control behavior, playback and recovery scenarios. Physical-device execution is only claimed when the exact device/build matrix is recorded.
- **API testing:** REST, HTTP, Postman, Swagger/OpenAPI, JSON Schema, request/response analysis and negative scenarios.
- **Automation:** Python, pytest, requests, JavaScript, Playwright and GitHub Actions.
- **Data and integration:** SQL, PostgreSQL, Docker Compose, service contracts, transactional invariants and controlled failure checks.

## Selected projects

This repository is the dedicated QA entry point. Selected projects, executable tests, documentation and CI evidence are maintained here; supporting labs are linked where they add distinct evidence.

| Project | Scope | Evidence |
|---|---|---|
| [Python API Automation](./api-automation) | REST client, pytest, schemas, negative cases, pagination and retry boundaries | 62 tests; successful CI matrix on Python 3.10 and 3.12 |
| [Booking API QA](./qa-cases/api-contract-negative) | Contract testing, validation, authorization, idempotency and state transitions | 31 tests; 100% statement coverage for the named `app.py` and `store.py` modules |
| [Checkout Regression](./qa-cases/checkout-regression) | Cart, pricing, promotions, stock boundaries and checkout UI | 24 Playwright scenarios |
| [FinTech QA Platform](./fintech-qa-platform) | Payment/Ledger integration, PostgreSQL, invariants, observability and recovery | Successful CI across quality, integration smoke and UI E2E jobs |
| [DWH Data Quality & ETL Testing](./dwh-data-quality-testing) | Airflow DAG, PostgreSQL raw/staging/core/mart, Python/SQL DQ gates, retries and reconciliation | Dedicated PostgreSQL CI workflow; Airflow orchestration documented and runnable locally |
| [Playwright QA Lab](https://github.com/blvxx/E2E-Automation) | Browser regression, accessibility, persistence and manual test design | 11 E2E tests and 20 documented manual cases |

## Data platform and ETL testing

[Open DWH Data Quality & ETL Testing Platform](./dwh-data-quality-testing) — layered warehouse, Airflow orchestration, pre-promotion DQ gate, idempotent replay and mart reconciliation. Cube REST API and dbt remain clearly marked as design-only extensions.

## QA engineering documents

- [QA Engineering Strategy](./qa-engineering-strategy.md) — risk prioritisation, test levels, traceability, defect lifecycle, quality gates and release recommendation.
- [Mobile / Android TV / Smart TV Checklist](./qa-mobile-tv-checklist.md) — device matrix, installation, lifecycle, network, remote navigation and media scenarios.
- [QA & Commercial Problem-Solving Casebook](./qa-commercial-casebook.md) — e-commerce, financial integrity, wholesale order intake and AI-assisted support cases.

## How I approach quality

1. Clarify requirements, acceptance criteria, dependencies and assumptions.
2. Prioritise scenarios by user impact, likelihood and data/business risk.
3. Select the right level of testing: API, integration, UI, manual exploratory or device.
4. Cover positive, negative, boundary, state-transition and recovery behavior.
5. Keep test data isolated and execution reproducible.
6. Investigate failures using requests, responses, browser traces, logs and device/build context.
7. Verify fixes, run focused regression and communicate residual risk.

## Business-oriented QA

I connect test coverage with business outcomes:

- **E-commerce:** prevent incorrect totals, promotion errors, stock issues and duplicate orders.
- **Financial workflows:** protect transaction integrity, idempotency and ledger consistency.
- **Wholesale operations:** concept for validating Excel/CSV orders before processing.
- **Support operations:** AI-assisted triage and runbook retrieval with human review.

These are implemented portfolio sandboxes and commercial solution concepts, not claims of paid client deployments or measured customer savings. The casebook explains the risks, proposed value and metrics needed to validate a real pilot.

## CI evidence

- [API Automation — 62 tests](https://github.com/blvxx/qa-engineering-labs/actions/workflows/api-automation.yml)
- [Booking API — 31 tests](https://github.com/blvxx/qa-engineering-labs/actions/workflows/qa-booking-api.yml)
- [Checkout Regression — 24 scenarios](https://github.com/blvxx/qa-engineering-labs/actions/workflows/qa-checkout-regression.yml)
- [FinTech QA Platform](https://github.com/blvxx/qa-engineering-labs/actions/workflows/fintech-qa-platform.yml)
- [Playwright QA Lab — 11 E2E tests](https://github.com/blvxx/E2E-Automation/actions/runs/45155361776)

**Coverage note:** the Booking API's 100% figure is statement coverage for two named modules only; it is not branch coverage, full requirements coverage or proof of production quality. A successful workflow verifies only the checks included in that run.

## Scope and transparency

The automated case studies are independent portfolio projects and practice environments. Payment, booking, checkout and incident scenarios are synthetic. Public demo APIs may simulate writes. The Booking API uses an in-memory store and simplified test authentication. The checkout app has no real payment or inventory backend. The mobile/TV checklist is a reusable test-design artifact; actual device compatibility should be stated against the exact device, OS/firmware and app build tested.

---

**Artem Kalinin** · [GitHub](https://github.com/blvxx)


## Detailed QA evidence index

[Open the QA Engineering Evidence Index](./docs/qa-engineering-evidence-index.md) for the consolidated reviewer guide: test ownership, strategy, project evidence, cross-platform coverage, API and integration testing, automation and limitations.

