# Checkout & Cart — Web QA Automation Case

<sub>Manual QA design · Playwright · Python · pytest · Chromium · browser traces · GitHub Actions</sub>

![Checkout E2E](https://github.com/blvxx/portfolio/actions/workflows/qa-checkout-regression.yml/badge.svg)

A self-contained web application and browser regression suite focused on the revenue-critical checkout path. It demonstrates risk-based test design, data-driven state transitions, price calculation assertions, form validation, duplicate-submit protection and responsive smoke testing.

> **Transparency:** Northstar Market is a fictional application authored for this portfolio. Prices, stock and orders are simulated. The suite does not claim to have tested a real merchant or payment system.

## At a glance

| Asset | Included |
|---|---|
| System under test | Responsive local storefront with cart and checkout |
| Browser automation | Playwright + Chromium |
| Test runner | pytest |
| Automated coverage | 24 browser scenarios |
| Test techniques | Positive, negative, boundary, state-transition, risk-based regression |
| Evidence | JUnit XML, Playwright traces, failure screenshots via CI artifact |

## What is being tested

- Cart add/remove, quantity boundaries and stock limits.
- Subtotal and line-total recalculation.
- Valid, expired and unknown promotions; protection against duplicate discount.
- Delivery and pickup cost transitions.
- Required checkout fields and email format.
- Delivery-specific address validation.
- Successful order confirmation and rapid duplicate submission.
- Mobile viewport overflow and programmatic form labels.

## Run locally

Python 3.10+ and a Chromium browser are required.

```bash
cd qa-cases/checkout-regression
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# macOS / Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m playwright install chromium
pytest -v
```

The suite loads repository HTML, CSS and JavaScript into an isolated browser page. It does not depend on a running backend or external service.

## Repository map

- `architecture.md`: application state model, browser test harness and explicit non-goals.
- `app/`: static responsive storefront and business rules.
- `tests/test_checkout.py`: 24 Playwright scenarios.
- `conftest.py`: browser lifecycle, fresh context per test, trace capture and failure screenshots.
- `test-plan.md`: risks, scope, data and exit criteria.
- `test-cases.md`: requirement-to-test traceability catalogue.
- `exploratory-charter.md`: complementary manual exploratory missions.
- `bug-reports.md`: examples of defect reports, clearly marked hypothetical.

## CI evidence

GitHub Actions runs the browser regression suite on relevant pushes and pull requests. The latest verified suite completed with **24 passed in Chromium (35 seconds)**: [GitHub Actions run](https://github.com/blvxx/portfolio/actions/runs/44993763830). The workflow uploaded the JUnit report and per-test Playwright traces as an evidence bundle: [download CI artifact](https://github.com/blvxx/portfolio/actions/runs/44993763830/artifacts/14742947149). Failure screenshots are also captured and uploaded when a test fails.

## Limitations

The app has no backend, database, payment provider or real inventory service. It does not demonstrate cross-browser coverage, production load, network resilience or payment certification. These are separate test layers that require a real environment.
