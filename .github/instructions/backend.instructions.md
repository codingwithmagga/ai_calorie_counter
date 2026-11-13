---
description: "Use when changing the FastAPI backend, Python tests, database models, migrations, or OpenAPI contract."
applyTo: "backend/**"
---

# Backend guidance

- Follow the existing Python, FastAPI, Pydantic, SQLAlchemy and Alembic
  patterns. Validate requests and define explicit response schemas; keep
  failures visible and avoid broad catches or silent fallbacks.
- For future private resources, derive identity from validated authentication
  and enforce ownership in server-side queries and mutations, including custom
  foods. Test access by another user and account deletion; neither auth nor
  user-owned data exists yet.
- When diary entries are implemented, persist immutable calorie and nutrient
  snapshots and test that later food edits do not rewrite history.
- Follow [development notes](../../docs/development.md) for `DATABASE_URL`,
  model registration, migration review and OpenAPI generation. There are no
  application models or migrations yet.
- From `backend/`, run `ruff check .`, `ruff format --check .`, and `pytest`
  for relevant changes. For API changes also regenerate both contract files
  and run the mobile checks in the
  [README](../../README.md#checks-and-api-contract); test affected endpoints
  and consumers.
- Update relevant documentation and instructions whenever behavior, commands,
  or architecture changes.
