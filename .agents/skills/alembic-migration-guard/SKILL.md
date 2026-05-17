# Skill: alembic-migration-guard

## Purpose

Use this skill when changing database schema or model structure.

## Scope

- SQLAlchemy model changes in `app/models`
- Alembic revision generation and review
- Migration safety checks

## Workflow

1. Confirm intended schema change and affected tables/columns.
2. Update SQLAlchemy models first.
3. Generate migration:
   - `uv run alembic revision --autogenerate -m "<message>"`
4. Review migration script manually for:
   - Correct table/column operations
   - Correct constraints/indexes
   - Safe downgrade behavior
5. Apply migration locally:
   - `uv run alembic upgrade head`
6. Run tests and required quality gates from `AGENTS.md`.

## Safety Rules

- Never modify production DB schema outside Alembic migrations.
- Keep migrations deterministic and reviewable.
- Avoid destructive schema actions unless explicitly required.

## Output Checklist

- Model update complete
- Migration script present and reviewed
- Migration applied successfully
- Tests and quality checks passed
