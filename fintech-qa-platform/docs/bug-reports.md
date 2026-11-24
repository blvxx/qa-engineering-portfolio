# Sample Bug Report Templates

These are templates for documenting defects found while executing the test plan. They are not claims that the listed defects exist in this implementation.

## Template

- ID:
- Title:
- Environment:
- Build / commit:
- Severity / priority:
- Preconditions:
- Steps to reproduce:
- Actual result:
- Expected result:
- Evidence: request/response, logs, SQL query, screenshot
- Regression scope:

## Example format (illustrative only)

- ID: BUG-EXAMPLE-001
- Title: Duplicate transfer is created after retry
- Environment: Local Docker Compose
- Severity / priority: Critical / High
- Preconditions: A transfer has already been accepted.
- Steps: Repeat the same request with the same idempotency key.
- Actual result: To be recorded only if observed during execution.
- Expected result: The original transfer is returned and account balances remain unchanged.
- Evidence: Capture both responses and account balance queries.

The example describes a test objective, not an observed defect.
