# Code Guidelines

This document defines development standards for this repository.

## 1. Core Principles

- Prioritize readability over cleverness.
- Keep functions small and focused on one responsibility.
- Prefer explicit behavior and predictable control flow.
- Preserve backward-compatible API behavior unless change is intentional.

## 2. Language and Communication

- Use English for:
  - Code comments
  - Docstrings
  - Error messages
  - Logs
  - Documentation

## 3. Python Style

- Follow Ruff formatting and linting rules from `pyproject.toml`.
- Target Python 3.11+ features already used by the project.
- Use type hints for all public functions and non-trivial internal helpers.
- Avoid wildcard imports.
- Avoid unused variables and dead code.
- Keep each `.py` file at a maximum of 500 LOC.
- Keep each function at a maximum of 300 LOC.

## 4. FastAPI Conventions

- Define request/response payloads in `app/schemas`.
- Keep route handlers thin; move reusable logic to service/helper layers when needed.
- Return typed response models for API consistency.
- Use dependency injection (`Depends`) for DB session and auth user.

## 5. Error Handling

- Raise `HTTPException` with clear, stable error messages for client-facing errors.
- Catch database exceptions (`SQLAlchemyError`) at route boundaries.
- Roll back transactions on write failures before returning errors.
- Log failures with enough context (`user_id`, `note_id`, etc.) without leaking secrets.

## 6. Security Rules

- Never store plain-text passwords; always hash before save.
- Never log passwords, tokens, or secrets.
- Validate and parse JWT tokens strictly.
- Keep security-sensitive config in environment variables.

## 7. Database and Migrations

- Keep SQLAlchemy models and Alembic migrations aligned.
- Use Alembic for all schema changes; do not patch DB schema manually in production workflows.
- Maintain deterministic seed behavior (idempotent inserts when possible).

## 8. Testing Expectations

- Add or update tests for every behavioral change.
- Cover happy path and at least key authorization/validation edge cases.
- Keep tests isolated and deterministic.

## 9. Logging

- Use module-level logger via `get_logger(__name__)`.
- Prefer structured and contextual log messages.
- Use levels consistently:
  - `info` for successful high-level events
  - `warning` for recoverable or client-caused issues
  - `exception` for unexpected server-side failures

## 10. Definition of Done

A task is complete only when:

1. Code changes are implemented.
2. Affected Python files pass:
   - `uv run -m ruff format [files]`
   - `uv run -m ruff check --fix [files]`
   - `uv run -m basedpyright [files]`
3. Full test suite passes:
   - `uv run -m pytest`
4. Relevant documentation is updated (`README.md`, `AGENTS.md`, this file when needed).
