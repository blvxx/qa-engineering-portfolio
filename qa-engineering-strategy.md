# QA Engineering Strategy — Artem Kalinin

**Focus:** risk-based quality engineering for API, web, mobile and transactional products  
**Portfolio level:** demonstrates middle-level QA responsibilities: test strategy, risk ownership, integration thinking, release criteria and evidence-based reporting.

> This is a reusable QA strategy authored for portfolio demonstration. It describes the approach applied to the portfolio sandboxes; it is not presented as a strategy approved or executed in a commercial client environment.

## 1. Quality objectives

Testing should answer four questions:

1. Does the product implement the expected business behavior?
2. Can the system preserve data integrity when users, services or networks behave unexpectedly?
3. Can a defect be reproduced, diagnosed and verified after a fix?
4. Is the remaining release risk visible to the people making the release decision?

The goal is not to maximise the number of test cases. The goal is to provide sufficient evidence for a risk-aware product decision.

## 2. Risk-based prioritisation

I prioritise a scenario using the model: **Risk = Impact × Likelihood**.

Both factors are assessed on a 1–5 scale. This is a lightweight prioritisation aid, not a statistically calibrated model.

| Risk band | Score | Test response |
|---|---:|---|
| Critical | 16–25 | Must be covered before release; include negative and recovery paths |
| High | 10–15 | Automate where stable; include in focused regression |
| Medium | 5–9 | Cover the main behavior and representative boundaries |
| Low | 1–4 | Check when relevant; document accepted residual risk |

Examples of high-impact risks:
- A repeated request creates a duplicate payment or order.
- A balance, price or ledger entry is calculated incorrectly.
- One user can read or modify another user's data.
- A migration silently drops, duplicates or transforms records incorrectly.
- A mobile or TV user becomes trapped because focus or navigation is lost.
- A degraded dependency causes data corruption instead of a controlled failure.

## 3. Test levels and responsibilities

| Level | Main purpose | Typical evidence |
|---|---|---|
| Unit / component | Validate isolated business rules and edge conditions | pytest results, deterministic fixtures |
| API / contract | Validate HTTP behavior, schema, authorization and error semantics | Postman collection, pytest, JSON Schema |
| Integration | Validate service boundaries, persistence and transaction invariants | Docker Compose, PostgreSQL assertions, integration logs |
| UI / E2E | Validate high-value user journeys and visible state | Playwright tests, screenshots, traces |
| Exploratory / manual | Find usability, workflow and interaction gaps not fully covered by automation | charter, notes, reproducible defect report |
| Operational / resilience | Validate observability, dependency failure and recovery | logs, metrics, controlled fault-injection evidence |

I use the test pyramid as a cost and feedback principle: keep fast API and component checks broad, and reserve slower end-to-end tests for the user journeys that justify their cost.

## 4. Requirements analysis and traceability

Before execution:

1. Identify actors, permissions, preconditions and expected state changes.
2. Separate business rules from UI behavior and technical constraints.
3. Record assumptions and unresolved questions instead of silently choosing an interpretation.
4. Map each important requirement or risk to at least one test scenario.
5. Mark scenarios as automated, manual, blocked or out of scope.

Useful techniques:
- Equivalence partitioning.
- Boundary value analysis.
- Decision tables.
- State-transition testing.
- Pairwise combinations when the input space is large.
- Negative testing and misuse cases.
- Risk-based regression selection.

Portfolio examples:
- [Booking API test matrix](./qa-cases/api-contract-negative/test-matrix.md)
- [Checkout test plan](./qa-cases/checkout-regression/test-plan.md)

## 5. API and integration strategy

For every endpoint or event flow, I consider:

- HTTP method, URL, headers, authentication and authorization.
- Required, optional, malformed and boundary input.
- Status code and error contract.
- Response schema, types, nullability and semantic consistency.
- Pagination, sorting, filtering and empty results.
- Duplicate requests, idempotency and retry safety.
- State before and after the operation.
- Dependency failures, timeout behavior and recovery.
- Data persistence and cross-service consistency where the environment allows it.

For transactional flows, I add invariants rather than checking only response codes. Examples include:
- Debits and credits balance for a completed ledger transaction.
- A replay with the same idempotency key does not create a second operation.
- A conflicting payload with a reused key is rejected.
- A failed dependency does not leave a partially completed business operation.
- A cancelled booking releases capacity according to the defined rule.

Tools represented in the portfolio: Python, pytest, requests, Postman, JSON Schema, FastAPI and PostgreSQL.

## 6. Web, mobile and TV strategy

### Web
- Validate behavior across supported browsers and viewport sizes.
- Inspect console errors, network requests, response payloads and browser storage.
- Check keyboard interaction, semantic labels, focus visibility and responsive overflow.
- Verify that UI state reflects the server response and handles delayed or failed requests.

### Android and iOS
- Cover install, first launch, upgrade, permissions and session lifecycle.
- Exercise foreground/background transitions, interruptions and application resume.
- Test connectivity changes, offline behavior, timeout and retry handling.
- Check device-specific layout, keyboard, orientation where supported, notifications and deep links.
- Verify that sensitive information is not exposed in logs or screenshots.

### Android TV and Smart TV
- Verify installation, launch, upgrade and clean-data behavior on the target device/firmware matrix.
- Test D-pad navigation, visible focus, focus order, Back behavior and focus recovery after dialogs or playback.
- Check remote key repeat, long press, center/select and unavailable keys.
- Validate player states: start, pause, seek, resume, buffering, error recovery and exit.
- Check audio track, subtitles, resolution changes and behavior after network interruptions.
- Record model, firmware, app build, connection type and reproducible steps for each finding.

A device compatibility claim is only as broad as the device/OS/firmware matrix actually executed. Emulator results do not replace physical-device checks.

See the [Mobile and TV QA checklist](./qa-mobile-tv-checklist.md).

## 7. Test data and environment control

- Use synthetic accounts and data in portfolio/demo environments.
- Make tests independent and repeatable; reset mutable state between cases.
- Avoid shared mutable fixtures that make execution order significant.
- Mask credentials and tokens in logs and attachments.
- Keep test and production environments separated.
- Record service versions, browser/device versions and environment dependencies.
- For migration checks, compare source and target counts, key uniqueness, required-field completeness, aggregates and sampled record-level values.

## 8. Defect lifecycle and communication

A useful defect report contains:

- Short, specific title.
- Environment and build.
- Preconditions and test data.
- Numbered reproduction steps.
- Expected versus actual result.
- Frequency and scope.
- Evidence: screenshot, request/response, logs or trace.
- Severity, business impact and suggested priority.

Severity describes technical/user impact; priority describes the order in which the team should address it. They are related but not interchangeable.

After a fix:
1. Reproduce the original issue on the affected build where possible.
2. Verify the fix on the candidate build.
3. Run focused regression around the changed component and its dependencies.
4. Record the build, result and any residual risk.

## 9. CI quality gates and release readiness

A release recommendation should be based on evidence, not on a green badge alone.

| Gate | Example acceptance condition |
|---|---|
| Build / static checks | Build completes; lint and type/static checks pass where configured |
| Critical API behavior | No known open blocker or critical defect in agreed scope |
| Contract and integration | Relevant contracts and critical state invariants pass |
| UI regression | Agreed critical journeys pass on the supported browser/device matrix |
| Test evidence | Reports, traces and failure details are available |
| Defect review | Open defects have severity, owner and documented disposition |
| Risk review | Untested areas, environment gaps and accepted risks are explicit |

Suggested status:
- **Go:** all mandatory gates pass; residual risk accepted by the owner.
- **Conditional go:** known non-blocking gaps are documented with owners and follow-up.
- **No-go:** a critical gate fails, data integrity is at risk, or a blocker remains unresolved.

The project owner makes the release decision. QA provides evidence and a risk recommendation.

## 10. Reporting that helps decisions

I prefer a compact report with:
- Scope and build/environment.
- Executed / passed / failed / blocked / not run.
- Critical scenarios and risks covered.
- New and reopened defects by severity.
- Evidence links.
- Known gaps and residual risk.
- Recommended next action.

Coverage percentages are always named precisely. Statement coverage is not branch coverage, requirement coverage or proof of defect absence.

## 11. Evidence in this portfolio

| Case | Demonstrated engineering practice |
|---|---|
| [API Automation](./api-automation/) | REST contracts, negative cases, pagination, timeout handling and safe retry boundaries |
| [Booking API QA](./qa-cases/api-contract-negative/) | Requirement traceability, authorization, idempotency, booking invariants and statement-coverage gate |
| [Checkout Regression](./qa-cases/checkout-regression/) | Revenue-critical UI path, calculations, promotion rules and duplicate-submit protection |
| [FinTech QA Platform](./fintech-qa-platform/) | Cross-service state, PostgreSQL, ledger invariants, observability and controlled recovery |
| [Playwright QA Lab](https://github.com/blvxx/playwright-qa-lab) | Browser regression, persistence, accessibility and manual test design |

## 12. Scope and limitations

The linked systems are independent portfolio sandboxes and synthetic business scenarios. Their successful CI runs prove only the checks included in those runs. They do not establish commercial client delivery, production certification, load/security coverage or validation on every physical mobile/TV device.

---

**Artem Kalinin** · [GitHub](https://github.com/blvxx) · [QA Portfolio](./qa-portfolio.md)
