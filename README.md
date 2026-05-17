# Notes Backend

FastAPI backend for a personal notes application with:
- JWT-based authentication
- Per-user note isolation
- Category-based note organization
- Pagination and search for notes and categories
- SQLAlchemy ORM + Alembic migrations

## Tech Stack

- Python 3.11+
- FastAPI
- SQLAlchemy 2.x
- Alembic
- PostgreSQL (default), SQLite supported for tests/local runs
- Ruff, BasedPyright, Pytest
- `uv` for dependency and command execution

## Project Structure

```text
.
|-- app/
|   |-- api/routes/          # auth, categories, notes routes
|   |-- core/                # config, logging, security helpers
|   |-- db/                  # SQLAlchemy base/session + seed utilities
|   |-- models/              # SQLAlchemy ORM models
|   `-- schemas/             # Pydantic request/response schemas
|-- alembic/                 # migration environment + revisions
|-- scripts/                 # operational scripts (category seeding)
|-- tests/                   # API tests
|-- main.py                  # app + DB exports
|-- pyproject.toml           # project and tooling config
`-- AGENTS.md                # agent execution rules for this repo
```

## Features

### Authentication

- `POST /register`: create user account
- `POST /login`: authenticate and return bearer token
- Bearer token is required for all notes and categories endpoints

### Categories

- `GET /categories`
- Query params:
  - `search` (optional, case-insensitive partial match)
  - `page` (default `1`)
  - `size` (default `10`, max `100`)

### Notes

- `GET /notes`: list authenticated user notes
- `GET /notes/{note_id}`: note detail for authenticated user
- `POST /notes`: create note
- `PUT /notes/{note_id}`: update note
- `DELETE /notes/{note_id}`: delete note
- Query params on list:
  - `search` (title/description)
  - `page`
  - `size`

## Data Model

- `users`
  - `id`, `name`, `email` (unique), `password` (bcrypt hash), `created_at`
- `categories`
  - `id`, `name` (unique)
- `notes`
  - `id`, `user_id` (FK users), `title`, `description`, `category_id` (FK categories), `created_at`, `updated_at`

Default categories:
- `work`
- `personal`
- `finance`
- `learning`
- `other`

## Configuration

Copy `.env.example` to `.env` and set values:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/notes
SECRET=replace-with-strong-random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120
LOG_LEVEL=INFO
APP_ENV=dev
```

Notes:
- `APP_ENV=prod` disables `/docs`, `/redoc`, and `/openapi.json`.
- `DATABASE_URL` can use SQLite for local testing (for example `sqlite:///./notes.db`).

## Setup

1. Install dependencies:

```bash
uv sync
```

2. Configure environment:

```bash
cp .env.example .env
```

3. Run migrations:

```bash
uv run alembic upgrade head
```

4. Seed default categories:

```bash
uv run python -m scripts.seed_categories
```

5. Run API:

```bash
uv run uvicorn main:app --reload
```

## Database Migration Workflow

- Create migration:

```bash
uv run alembic revision --autogenerate -m "your_message"
```

- Apply migration:

```bash
uv run alembic upgrade head
```

- Rollback last migration:

```bash
uv run alembic downgrade -1
```

## Testing and Code Quality

Run full checks:

```bash
uv run -m ruff format app tests scripts alembic main.py
uv run -m ruff check --fix app tests scripts alembic main.py
uv run -m basedpyright app tests scripts alembic main.py
uv run -m pytest
```

## API Behavior Guarantees (Current Tests)

- Registration and login flows work end-to-end
- Category listing supports pagination and search
- Notes CRUD works end-to-end
- Note visibility is isolated per authenticated user

## Security Notes

- Passwords are hashed with bcrypt
- JWT includes expiration claim (`exp`)
- Token validation is required for protected endpoints
- Keep `SECRET` strong and private in production

## Development Rules for Agents

- See `AGENTS.md` for mandatory agent execution workflow.
- See `CODE_GUIDELINES.md` for coding standards and implementation conventions.
