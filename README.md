# Artem Kalinin — QA Engineering Portfolio

**QA Engineer · Web & Mobile QA · Android TV / Smart TV · API Testing · Python Automation**

I work with functional, regression, exploratory and API testing, combining hands-on product testing with Python and Playwright automation. My focus is risk-based test design, reliable user journeys, data integrity, reproducible defect investigation and release confidence.

**Target roles:** QA Engineer · Manual QA Engineer · API Tester · QA Automation Engineer (Python) · Mobile QA Engineer

[GitHub profile](https://github.com/blvxx) · [Email](mailto:blvx8x@gmail.com) · [Telegram](https://t.me/blvlxx)

## Core QA capabilities

- **Web testing:** functional and regression testing, responsive behavior, Chrome DevTools (Elements, Console, Network, Application, Device Toolbar).
- **Mobile testing:** Android and iOS application flows, lifecycle, permissions, connectivity, sessions and error handling.
- **TV testing:** Android TV / Smart TV installation and verification, D-pad navigation, visible focus, remote-control behavior, playback and recovery.
- **API testing:** REST, HTTP, Postman, Swagger/OpenAPI, JSON Schema, request/response analysis and negative scenarios.
- **Automation:** Python, pytest, requests, JavaScript, Playwright and GitHub Actions.
- **Data and integration:** SQL, PostgreSQL, Docker Compose, service contracts, transactional invariants and controlled failure checks.

## Selected projects

The project implementations are currently maintained in the original engineering repository. This repository is the dedicated QA entry point; links below open the source code and evidence.

| Project | Scope | Evidence |
|---|---|---|
| [Python API Automation](https://github.com/blvxx/portfolio/tree/main/api-automation) | REST client, pytest, schemas, negative cases, pagination and retry boundaries | 62 tests; successful CI matrix on Python 3.10 and 3.12 |
| [Booking API QA](https://github.com/blvxx/portfolio/tree/main/qa-cases/api-contract-negative) | Contract testing, validation, authorization, idempotency and state transitions | 31 tests; 100% statement coverage for the named `app.py` and `store.py` modules |
| [Checkout Regression](https://github.com/blvxx/portfolio/tree/main/qa-cases/checkout-regression) | Cart, pricing, promotions, stock boundaries and checkout UI | 24 Playwright scenarios |
| [FinTech QA Platform](https://github.com/blvxx/portfolio/tree/main/fintech-qa-platform) | Payment/Ledger integration, PostgreSQL, invariants, observability and recovery | Successful CI across quality, integration smoke and UI E2E jobs |
| [Playwright QA Lab](https://github.com/blvxx/playwright-qa-lab) | Browser regression, accessibility, persistence and manual test design | 11 E2E tests and 20 documented manual cases |

## QA engineering documents

- [QA Engineering Strategy](https://github.com/blvxx/portfolio/blob/main/qa-engineering-strategy.md) — risk prioritisation, test levels, traceability, defect lifecycle, quality gates and release recommendation.
- [Mobile / Android TV / Smart TV Checklist](https://github.com/blvxx/portfolio/blob/main/qa-mobile-tv-checklist.md) — device matrix, installation, lifecycle, network, remote navigation and media scenarios.
- [QA & Commercial Problem-Solving Casebook](https://github.com/blvxx/portfolio/blob/main/qa-commercial-casebook.md) — e-commerce, financial integrity, wholesale order intake and AI-assisted support cases.

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

- [API Automation — 62 tests](https://github.com/blvxx/portfolio/actions/runs/45102695248)
- [Booking API — 31 tests](https://github.com/blvxx/portfolio/actions/runs/44993766677)
- [Checkout Regression — 24 scenarios](https://github.com/blvxx/portfolio/actions/runs/44993763830)
- [FinTech QA Platform](https://github.com/blvxx/portfolio/actions/runs/45100258032)
- [Playwright QA Lab — 11 E2E tests](https://github.com/blvxx/playwright-qa-lab/actions/runs/45155361776)

**Coverage note:** the Booking API's 100% figure is statement coverage for two named modules only; it is not branch coverage, full requirements coverage or proof of production quality. A successful workflow verifies only the checks included in that run.

## Scope and transparency

The automated case studies are independent portfolio projects and practice environments. Payment, booking, checkout and incident scenarios are synthetic. Public demo APIs may simulate writes. The Booking API uses an in-memory store and simplified test authentication. The checkout app has no real payment or inventory backend. The mobile/TV checklist is a reusable test-design artifact; actual device compatibility should be stated against the exact device, OS/firmware and app build tested.

---

**Artem Kalinin** · [GitHub](https://github.com/blvxx)
