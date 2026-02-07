# AGENTS.md
Agent instructions for this repository.

## Scope
- Applies to all code changes in this repo.
- Prioritize minimal, task-focused edits.
- Follow existing Django conventions unless task says otherwise.

## Project Overview
- Framework: Django 5 (`Django==5.0.6`).
- Runtime target: Python 3.11 (`runtime.txt`).
- WSGI app: `mysite.wsgi`.
- Static handling: WhiteNoise middleware enabled.
- Database: SQLite (`db.sqlite3` in project root).
- Deployment hint: `railway.json` runs migrate + collectstatic + gunicorn.
- Current codebase is a starter project with no custom apps yet.

## Environment Setup
Use `python3` commands in this environment.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

No database environment variables are required for local development.

## Build, Lint, and Test Commands
There is no formal compile step; use Django checks as build-equivalent validation.

### Development run
```bash
python3 manage.py migrate
python3 manage.py runserver
```

### Build-equivalent checks
```bash
python3 manage.py check
python3 manage.py collectstatic --noinput
```

### Tests
Run all tests:

```bash
python3 manage.py test
```

Run one module:

```bash
python3 manage.py test myapp.tests
```

Run one test class:

```bash
python3 manage.py test myapp.tests.TestCheckoutFlow
```

Run one test method (preferred single-test pattern):

```bash
python3 manage.py test myapp.tests.TestCheckoutFlow.test_rejects_expired_card
```

Use dotted test labels for precise and reproducible targeting.

### Lint / format
- No linter or formatter is configured in this repo today.
- If task requires linting and tool exists in environment, prefer:
  1) `ruff check .`
  2) `ruff format .` (or `black .` if repo adopts Black)
- Do not introduce new tooling unless task asks for it.

## Code Style Guidelines
Follow PEP 8 and Django best practices, matching nearby code.

### Imports
- Order groups: standard library, third-party, local.
- Keep one blank line between import groups.
- Prefer explicit imports; avoid wildcard imports.
- Keep imports at top-level unless lazy import is necessary.

### Formatting
- Use 4-space indentation; no tabs.
- Keep lines readable (target 88-100 chars, consistent per file).
- Keep quote style consistent with file (current files mostly use single quotes).
- Keep multiline literals with trailing commas when it improves diffs.
- End files with exactly one newline.

### Types
- Add type hints for new non-trivial functions.
- Add return types for helpers and utility functions.
- Avoid unnecessary annotations for obvious local variables.
- Keep typing pragmatic; readability first.

### Naming
- Modules/functions/variables: `snake_case`.
- Classes/exceptions: `PascalCase`.
- Constants/settings: `UPPER_SNAKE_CASE`.
- URL names should be stable and descriptive.

### Django architecture
- Keep URLconfs thin; route logic to views/services.
- Keep business rules out of settings and URL modules.
- Prefer ORM APIs; use raw SQL only with clear need.
- Keep migrations generated and checked in with model changes.

### Error handling
- Fail fast for missing config and invalid runtime assumptions.
- Catch specific exceptions, not broad `Exception`.
- Re-raise with context when translating low-level errors.
- Never expose secrets in error responses.
- Use actionable messages in management commands.

### Logging
- Use Django/Python logging for runtime diagnostics.
- Avoid `print` in application code.
- Include context IDs when useful.
- Never log secrets, passwords, tokens, or private keys.

### Tests and quality expectations
- Add or update tests for behavior changes.
- Prefer focused unit tests; use integration tests for DB-heavy behavior.
- Name tests by behavior (e.g., `test_returns_403_for_anonymous_user`).
- When fixing bugs, add a failing regression test first when feasible.
- Run the smallest relevant test scope before finalizing.

## Security and Config Notes
- Treat current `SECRET_KEY` as non-production placeholder.
- Do not commit `.env` files or credentials.
- Keep `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` environment-appropriate.
- Do not commit `db.sqlite3` unless the task explicitly requests it.
- Preserve WhiteNoise middleware behavior when changing static settings.

## Cursor and Copilot Rules
Checked for additional agent instructions in:
- `.cursor/rules/`
- `.cursorrules`
- `.github/copilot-instructions.md`

Result: none of these files exist in this repository currently.
If added later, treat them as higher-priority repository rules.

## Agent Workflow Expectations
- Read related files before editing.
- Keep diffs small and avoid unrelated refactors.
- Prefer backward-compatible changes unless task requests breaking updates.
- Run relevant checks/tests for touched code.
- In handoff notes, include what was run and what could not be run.
