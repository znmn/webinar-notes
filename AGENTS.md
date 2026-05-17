# AGENTS Guidelines

All coding agents working in this repository must follow `CODE_GUIDELINES.md`.

After writing or modifying Python code, agents **must** run the following steps for the changed Python files (`[files]`) in this exact order:

1. `uv run -m ruff format [files]`
2. `uv run -m ruff check --fix [files]`
3. `uv run -m basedpyright [files]`
4. `uv run -m pytest`

## Rules

- `[files]` means the list of Python files created or modified in the current task.
- Do not skip any step.
- If any step fails, fix the issue and rerun from step 1 through step 4.
- Keep all agent-facing and user-facing content in English.
