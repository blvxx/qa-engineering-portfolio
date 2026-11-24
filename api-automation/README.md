# API Automation — Python, pytest, requests

[![API Automation](https://github.com/blvxx/portfolio/actions/workflows/api-automation.yml/badge.svg)](https://github.com/blvxx/portfolio/actions/workflows/api-automation.yml)

Portfolio project demonstrating REST API test automation: a reusable HTTP client, CRUD request coverage, strict JSON Schema checks, parametrized positive and negative scenarios, isolated unit tests, a Postman collection, static analysis, Allure labels, and GitHub Actions CI.

> This is an independent portfolio project against the public JSONPlaceholder demo API. It is not a commercial client delivery or a production API contract.

## Coverage

| Area | Scenarios |
|---|---|
| Read | `GET /posts`, `GET /posts/{id}`, `GET /posts/{id}/comments`, response status, content type, filtering and response schema |
| Create | `POST /posts`, request payload validation, `201 Created`, generated ID and response fields |
| Replace | `PUT /posts/{id}`, full JSON payload and response contract |
| Partial update | `PATCH /posts/{id}`, partial JSON payload and updated resource representation |
| Delete | `DELETE /posts/{id}`, successful deletion response |
| Negative | Unknown IDs, invalid filters, incorrect types, missing fields and unexpected request/response properties |
| Unit | HTTP method, URL, headers, query parameters, JSON body, timeout propagation, environment configuration and owned/borrowed session lifecycle |
| Transport | Loopback HTTP fault injection verifies that transient GET failures retry while POST writes are never replayed |
| Postman | Importable collection with read, CRUD and negative requests plus response assertions |

## Test design

- API behavior tests call a public demo endpoint and require internet access.
- API-client unit tests use mocked `requests.Session` objects and do not require network access.
- Positive, negative and CRUD scenarios are grouped with pytest markers.
- Post and comment response payloads plus create-request bodies are validated against JSON Schema (Draft 2020-12).
- Nested-resource tests verify that comment records belong to the requested parent post.
- Parametrization checks several values without duplicating test functions.
- Allure feature/story labels and JSON attachments make request/response evidence easier to inspect.
- Ruff checks the Python code for common errors and unused imports.
- The Postman collection mirrors the main Posts API scenarios for manual execution.
- Transport exceptions such as request timeouts are not swallowed by the client.
- A deterministic local HTTP server verifies real adapter behavior for retryable reads and non-retryable writes without relying on an external API.
- Injected `requests.Session` objects remain caller-owned; the client closes only sessions it creates.

## Client resilience features

The reusable client supports optional bearer-token configuration through `bearer_token` or the `API_BEARER_TOKEN` environment variable. When it creates its own session, it retries transient connection and selected HTTP status failures for **GET / HEAD / OPTIONS only**. It does not automatically retry write methods, avoiding duplicate side effects. A bounded `iter_posts(page_size, max_pages)` helper demonstrates pagination and validates response shapes.

The authentication option is for a compatible protected test environment configured through `API_BASE_URL`; the public JSONPlaceholder demo does not require a token.

Additional isolated tests in `tests/test_client_resilience.py` cover token handling, safe retry configuration, pagination boundaries and invalid options.

## Test documentation

- [Test Plan](docs/test-plan.md) — scope, test types, environment, test data, risks, entry/exit criteria and coverage traceability.

## Postman collection

Import [`postman/JSONPlaceholder-Posts.postman_collection.json`](postman/JSONPlaceholder-Posts.postman_collection.json) into Postman. It contains GET, filtering, POST, PUT, PATCH, DELETE and a negative 404 check with built-in test scripts. See the [Postman import notes](postman/README.md).

## Important limitation of the demo API

JSONPlaceholder simulates write operations. A successful `POST`, `PUT`, `PATCH` or `DELETE` response demonstrates the HTTP contract, but the change is not persisted in the server's data. For example, a created post may be returned with an ID, but fetching that generated ID later still returns 404. This is expected demo-service behavior, not a defect in the test suite.

See the [official JSONPlaceholder guide](https://jsonplaceholder.typicode.com/guide.html) for examples and the write-operation limitation.

## Tech stack

- Python 3.10+
- pytest
- requests
- jsonschema
- allure-pytest
- Postman
- Ruff
- GitHub Actions

## Run locally

From the repository root, enter the project directory, then create and activate a virtual environment:

```bash
cd api-automation
python -m venv .venv

# Windows PowerShell
.venv\\Scripts\\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

Install runtime and development dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
```

Run static checks:

```bash
ruff check api_client.py tests/
```

Run the complete suite:

```bash
pytest -ra
```

Run tests that do not call the external API:

```bash
pytest -m unit
```

Run CRUD scenarios only:

```bash
pytest -m crud
```

Run the smoke checks:

```bash
pytest -m smoke
```

Generate JUnit and Allure result files:

```bash
pytest --junitxml=reports/junit.xml --alluredir=allure-results
```

## Configuration

The default base URL is `https://jsonplaceholder.typicode.com`. Override it without editing source code:

```bash
# macOS / Linux
export API_BASE_URL=https://your-test-environment.example

# Windows PowerShell
$env:API_BASE_URL = "https://your-test-environment.example"
```

The client also accepts `base_url` in its constructor. The request timeout defaults to 10 seconds and can be set when creating the client.

## CI

GitHub Actions runs static checks, isolated unit tests and the complete suite on Python 3.10 and 3.12 when files under `api-automation/` or the workflow change. JUnit and Allure result files are uploaded as artifacts, including when tests fail.

- [Latest workflow runs](https://github.com/blvxx/portfolio/actions/workflows/api-automation.yml)
- [Workflow definition](../../.github/workflows/api-automation.yml)

Check the Actions tab for the actual result of each run; workflow configuration alone does not prove that a run passed.

### Latest verified CI evidence

The latest reviewed run on **23 November 2026** completed successfully on both supported Python versions: **3.10 and 3.12**. Each matrix job passed Ruff, **26 isolated unit tests**, and the complete **62-test API suite**. This includes the loopback HTTP transport fault-injection check. Both versions uploaded JUnit and Allure results.

[Open the successful CI run](https://github.com/blvxx/portfolio/actions/runs/45102695248) · [Python 3.10 report bundle](https://github.com/blvxx/portfolio/actions/runs/45102695248/artifacts/14786485505) · [Python 3.12 report bundle](https://github.com/blvxx/portfolio/actions/runs/45102695248/artifacts/14785513694)

## Project structure

```text
api-automation/
├── api_client.py
├── pytest.ini
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── .gitignore
├── docs/
│   └── test-plan.md
├── schemas/
│   ├── post.schema.json
│   ├── post-create-request.schema.json
│   └── comment.schema.json
├── postman/
│   ├── JSONPlaceholder-Posts.postman_collection.json
│   └── README.md
└── tests/
    ├── test_api_client.py
    ├── test_client_resilience.py
    ├── test_http_transport.py
    └── test_posts_api.py
```

## Known limitations and next steps

- The public demo API may be temporarily unavailable or slow; live API tests can therefore fail because of external conditions.
- Demo write operations are not persistent and must not be treated as database persistence checks.
- The project currently focuses on the Posts resource; the optional bearer-token setting demonstrates client configuration, not a verified authorization flow against the public demo API.
- No database, load, security or production end-to-end coverage is claimed.
- Future extensions can add contract drift checks against an owned, versioned API contract and broader pagination edge cases.

## Maintainer

Artem Kalinin — [GitHub profile](https://github.com/blvxx)
