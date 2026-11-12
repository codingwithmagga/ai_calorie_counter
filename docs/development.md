# Development

The current monorepo contains a placeholder Expo Router screen, a FastAPI health endpoint, a PostgreSQL Compose service and an empty Alembic environment. Authentication, user data and food integrations are not implemented.

Follow the [README](../README.md) to start the services and run checks. The Compose database is for local development only and persists in a Docker volume. `docker compose down -v` deletes that local data.

Run migrations from `backend` with `DATABASE_URL` set. Define future SQLAlchemy models using `app.database.Base`, import those models in `migrations/env.py` before autogenerating a revision, then review the generated migration before applying it. There are currently no application tables or migrations.

Generate the OpenAPI snapshot with `python -m app.export_openapi` in `backend`, then run `npm run generate-api` in `mobile`. Commit both outputs; CI checks the snapshot and generated types. For a JavaScript bundle smoke build, run `npx expo export --platform android` in `mobile`; real device builds and distribution require the Expo/EAS tooling and platform configuration.

The scoped `minimatch` overrides in `mobile/package.json` address GHSA-g3hv-75wg-m249 in development tooling. Revisit them when upstream dependencies support a patched version; verify lint, generation and Expo export when changing them.
