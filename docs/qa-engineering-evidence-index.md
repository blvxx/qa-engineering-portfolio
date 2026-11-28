# QA Engineering Evidence Index — QA Engineering

**Purpose:** evidence index for QA engineering projects. The single employer-facing career portfolio is [here](https://blvxx.github.io/portfolio/).

I combine functional, regression, exploratory and API testing with Python/Playwright automation and hands-on web, mobile and TV application testing. My focus is product risk, data integrity, test strategy, cross-layer investigation and evidence-based release decisions.

> This document is a technical evidence index, not a separate career portfolio. Use the [single employer-facing portfolio](https://blvxx.github.io/portfolio/) for the overall professional introduction; use this file to navigate QA project details.

**[GitHub Profile](https://github.com/blvxx)** · [Main Engineering Portfolio](./README.md) · [Email](mailto:blvx8x@gmail.com) · [Telegram](https://t.me/blvlxx)

## What I bring

- **Test ownership:** requirement analysis, scope definition, test planning, risk prioritisation, traceability and release recommendations.
- **Manual QA:** functional, regression, exploratory, acceptance, negative, boundary and state-transition testing.
- **Product coverage:** web applications, Android, iOS, Android TV and Smart TV scenarios.
- **API and integration:** REST, HTTP, Postman, Swagger/OpenAPI, Charles/Proxyman traffic analysis, SQL and PostgreSQL.
- **Automation:** Python, pytest, requests, JavaScript, Playwright and GitHub Actions.
- **Diagnostics:** Chrome DevTools, browser storage, network inspection, logs, test traces and Android build/device diagnostics.

## Evidence at a glance

| Area | Evidence | What it demonstrates |
|---|---|---|
| API automation | [Python API Automation](./api-automation/) — 62 tests; CI on Python 3.10 and 3.12 | REST CRUD, JSON Schema, positive/negative cases, pagination, timeouts, safe retry boundaries |
| API quality / test design | [Booking API QA Sandbox](./qa-cases/api-contract-negative/) — 31 tests; 100% statement coverage for app.py and store.py | Risk-based coverage, authorization, idempotency, booking invariants, boundary validation and traceability |
| Web checkout regression | [Checkout & Cart QA](./qa-cases/checkout-regression/) — 24 Playwright scenarios | Revenue-critical flows, calculations, promotions, stock limits, form validation and duplicate-submit protection |
| UI automation + manual QA | [Playwright QA Lab](https://github.com/blvxx/E2E-Automation) — 11 E2E tests and 20 documented manual cases | Browser regression, accessibility checks, persistence, responsive smoke and defect documentation |
| Integration / system QA | [FinTech QA Platform](./fintech-qa-platform/) | API and service integration, PostgreSQL, Docker Compose, ledger invariants, browser flows and observability |

## Featured case studies

### 1. Python API Automation

**Stack:** Python · pytest · requests · JSON Schema · Postman · Allure · GitHub Actions

A reusable REST client and automated suite against the public JSONPlaceholder demo API, complemented by isolated client tests and deterministic local HTTP fault injection.

- CRUD methods and response contracts for Posts and Comments.
- Positive, negative and parametrized validation scenarios.
- JSON Schema checks for request and response payloads.
- Pagination boundaries, timeout propagation and malformed response handling.
- Retry policy verifies that transient read requests can retry while write requests are not automatically replayed.
- Importable Postman collection and CI reporting.

**Evidence:** [README and test plan](./api-automation/) · [Successful CI run — 23 Nov 2026](https://github.com/blvxx/portfolio/actions/runs/45102695248)

**Boundary:** JSONPlaceholder simulates writes; successful POST/PUT/PATCH/DELETE responses do not prove persistent server-side changes. The suite does not claim production authentication, database, load or security coverage.

### 2. Booking API — Contract and Negative Testing

**Stack:** Python · FastAPI · pytest · Pydantic · coverage · GitHub Actions

A self-contained API and test suite for a fictional booking service.

- 31 automated test cases.
- 100% statement coverage for the authored app.py and store.py modules in the verified run.
- Contract checks for status codes, response fields and pagination.
- Boundary and negative scenarios for dates, capacity and invalid payloads.
- Authorization and cross-user access checks.
- Overlapping reservations, cancellation and idempotency replay.
- Requirement-to-test traceability and hypothetical defect examples, clearly labelled as such.

**Evidence:** [Project README](./qa-cases/api-contract-negative/) · [Test matrix](./qa-cases/api-contract-negative/test-matrix.md) · [Successful CI run — 22 Nov 2026](https://github.com/blvxx/portfolio/actions/runs/44993766677)

**Boundary:** the API uses an isolated in-memory store and simplified test-token authentication. It does not verify database transactions, distributed concurrency or a production identity provider. 100% statement coverage is not the same as 100% branch or requirements coverage.

### 3. Checkout & Cart — Browser Regression

**Stack:** Python · pytest · Playwright · Chromium · GitHub Actions

A fictional storefront used to test a revenue-critical checkout workflow.

- 24 automated browser scenarios.
- Cart quantity and stock boundaries.
- Subtotal, discount and delivery-cost calculations.
- Valid, expired and unknown promotions.
- Required-field and email validation.
- Delivery / pickup state transitions.
- Successful confirmation and rapid duplicate-submit protection.
- Responsive layout and accessible form labels.
- CI retains JUnit results, traces and failure screenshots.

**Evidence:** [Project README](./qa-cases/checkout-regression/) · [Test plan](./qa-cases/checkout-regression/test-plan.md) · [Test cases](./qa-cases/checkout-regression/test-cases.md) · [Successful CI run — 22 Nov 2026](https://github.com/blvxx/portfolio/actions/runs/44993763830)

**Boundary:** the storefront, product catalogue and order confirmation are simulated. No real payment gateway, inventory backend or shipping provider is connected.

### 4. Playwright UI Automation Lab

**Stack:** JavaScript · Playwright · Chromium · GitHub Actions

A browser-based task tracker used for UI test design and accessibility regression.

- 11 automated end-to-end scenarios.
- 20 documented manual test cases and one exploratory responsive check.
- Empty/whitespace validation, keyboard submission, completion, deletion and persistence.
- Accessible names and semantic label interaction.
- Malformed local-storage recovery.
- Two accessibility findings documented, fixed in the sample application and covered by regression tests.

**Evidence:** [Repository](https://github.com/blvxx/E2E-Automation) · [Manual test cases](https://github.com/blvxx/E2E-Automation/blob/main/docs/test-cases.md) · [Execution report](https://github.com/blvxx/E2E-Automation/blob/main/docs/test-execution-report.md) · [Successful CI run — 23 Nov 2026](https://github.com/blvxx/E2E-Automation/actions/runs/45155361776)

**Execution note:** the manual report records an isolated Chromium harness run. The report documents the local-file navigation restriction and storage shim; native browser persistence is separately exercised by the Playwright CI suite. It is not presented as a user-operated production test session.

### 5. FinTech QA Engineering Platform

**Stack:** Python · FastAPI · pytest · Playwright · PostgreSQL · Docker Compose · Prometheus · Grafana

A fictional payment and ledger sandbox used to exercise API and service-integration behavior.

- Payment and Ledger service flows.
- Ledger debit/credit invariants and idempotent retry checks.
- PostgreSQL-backed integration tests.
- Docker Compose smoke checks and browser-level flows.
- Observability and a guarded dependency-outage/recovery drill.

**Evidence:** [Project overview](./fintech-qa-platform/overview.html) · [Source and setup](./fintech-qa-platform/) · [Successful CI run — 23 Nov 2026](https://github.com/blvxx/portfolio/actions/runs/45100258032)

**Boundary:** payment providers and business transactions are simulated. This is a QA sandbox, not a deployed financial product or production certification.

## Mobile, Android TV and Smart TV testing

I also work with mobile and television application scenarios. The device-specific approach is documented in the [Mobile / Android TV / Smart TV QA Checklist](./qa-mobile-tv-checklist.md), which covers:

- Installation, first launch, updates and clean-data behavior.
- Android and iOS lifecycle, permissions, notifications and deep links.
- Network changes, offline states, timeouts and safe retries.
- Android TV / Smart TV D-pad navigation, focus order, Back behavior and remote key handling.
- Media playback, buffering, seek, audio tracks and subtitles.
- Device/OS/firmware matrix, build identification and defect evidence.

Compatibility claims should always identify the exact models, OS/firmware and builds actually tested.

## QA strategy and release ownership

The [QA Engineering Strategy](./qa-engineering-strategy.md) describes my approach to:

- Risk-based test prioritisation and test pyramid.
- Requirements decomposition and traceability.
- API, integration, web and device test design.
- Test data, defect lifecycle and fix verification.
- CI quality gates, release readiness and residual-risk reporting.

## Business-oriented QA and commercial ideas

The [QA & Commercial Problem-Solving Casebook](./qa-commercial-casebook.md) connects quality work to business outcomes and records solution concepts around:

- E-commerce checkout and order correctness.
- Financial transaction and ledger integrity.
- Wholesale Excel/CSV order-intake validation.
- AI-assisted support triage and runbook retrieval.

The casebook separates implemented portfolio prototypes from commercial concepts and identifies the metrics needed to validate business value in a real pilot. It does not claim unverified revenue, paid client delivery or customer savings.

## Tools

**Manual and product QA:** functional · regression · exploratory · acceptance · mobile · Android TV / Smart TV · test plans · test cases · defect management  
**Web and device diagnostics:** Chrome DevTools · Elements · Console · Network · Application · Device Toolbar · ADB  
**API and data:** HTTP · REST · Postman · Swagger / OpenAPI · JSON · JSON Schema · Charles · Proxyman · SQL · PostgreSQL  
**Automation:** Python · pytest · requests · Playwright · JavaScript  
**Delivery:** Git · GitHub Actions · Docker Compose · Allure · JUnit XML · Playwright traces · logs · metrics

## CI evidence

Selected runs reviewed on 23 November 2026:

- [API Automation](https://github.com/blvxx/portfolio/actions/runs/45102695248) — 62 tests passed on Python 3.10 and 3.12.
- [Booking API QA](https://github.com/blvxx/portfolio/actions/runs/44993766677) — 31 tests; 100% statement coverage on app.py and store.py.
- [Checkout Regression](https://github.com/blvxx/portfolio/actions/runs/44993763830) — 24 browser scenarios passed.
- [FinTech QA Platform](https://github.com/blvxx/portfolio/actions/runs/45100258032) — quality, Compose smoke and UI E2E jobs passed.
- [Playwright QA Lab](https://github.com/blvxx/E2E-Automation/actions/runs/45155361776) — 11 browser E2E tests passed.

## Additional engineering background

For QA roles close to support and production troubleshooting:
- [Linux Support Engineering Lab](./support-engineering-lab/) — 10 troubleshooting playbooks, log triage and evidence capture.
- [Incident Investigation Lab](./incident-lab/) — simulated incident timeline, SQL reconciliation, RCA and recovery runbooks.
- [Support Operations Analytics](./support-operations-analytics/) — ticket, SLA and workload analysis.

---

**Artem Kalinin** · [GitHub](https://github.com/blvxx) · [Email](mailto:blvx8x@gmail.com) · [Telegram](https://t.me/blvlxx)
