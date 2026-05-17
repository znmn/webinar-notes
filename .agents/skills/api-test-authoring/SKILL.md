# Skill: api-test-authoring

## Purpose

Use this skill to add or update API tests for this backend.

## Scope

- Test additions/changes under `tests/`
- Authentication and authorization scenarios
- CRUD, pagination, and search behavior validation

## Workflow

1. Identify behavior change and expected API contract.
2. Add or update tests in `tests/` using `fastapi.testclient.TestClient`.
3. Keep tests deterministic:
   - Isolated test DB setup/teardown
   - No dependency on test execution order
4. Cover both success and failure paths where relevant.
5. Run full checks from `AGENTS.md`.

## Test Design Rules

- Assert status codes and key response payload fields.
- Validate per-user data isolation for protected resources.
- Keep fixtures/helpers minimal and readable.

## Output Checklist

- Test coverage updated for changed behavior
- Tests pass locally
- No regressions in existing tests
