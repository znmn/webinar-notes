# Skill: fastapi-backend-dev

## Purpose

Use this skill when implementing or modifying backend API features in this repository.

## Scope

- FastAPI route changes in `app/api/routes`
- Pydantic schema updates in `app/schemas`
- SQLAlchemy model integration in `app/models`
- Auth-protected endpoint behavior

## Workflow

1. Read impacted route, schema, and model files before editing.
2. Keep route handlers concise; preserve existing response model patterns.
3. Validate ownership boundaries for user data (never expose cross-user notes).
4. Update tests for behavior changes in `tests/`.
5. Run required quality gates from `AGENTS.md`.

## Repository Rules

- Follow `CODE_GUIDELINES.md`.
- Keep all comments, docstrings, logs, and error messages in English.
- Prefer explicit error handling with `HTTPException`.

## Output Checklist

- Endpoint behavior implemented
- Request/response schemas updated if needed
- Tests added or updated
- Quality checks completed successfully
