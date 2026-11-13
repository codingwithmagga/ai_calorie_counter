# Architecture

This document describes the current Phase 0 implementation separately from
the target design. The [project specification](./PROJECT_SPEC.md) is the
planning baseline for product scope and future requirements; the
[development notes](./development.md) describe local commands.

## Implemented today

```text
Expo Router app                    HTTP client (not used by the screen)
  app/_layout.tsx -> app/index.tsx   createApiClient(baseUrl)
                                            |
                                            | may call API when used
                                            v
                                   FastAPI GET /health -> {"status": "ok"}

OpenAPI: FastAPI -> backend/openapi.json -> mobile/src/api/schema.d.ts
Local migrations: Alembic + DATABASE_URL -> PostgreSQL (Compose)
```

- **Mobile:** Expo Router renders a static placeholder screen. The
  `openapi-fetch` client accepts a caller-provided base URL and uses generated
  TypeScript types, but the screen does not instantiate it or call the API.
  Generated types do not validate response bodies at runtime.
- **Backend:** `app/main.py` defines the FastAPI application and its only
  application endpoint, `GET /health`, with a Pydantic response model. FastAPI
  exposes its interactive API documentation at `/docs`.
- **Persistence:** Compose provides a local PostgreSQL service, bound to
  `127.0.0.1`, with a named volume and development-only credentials. Alembic
  requires `DATABASE_URL` and uses `app.database.Base` metadata. There are no
  application models or migration revisions; the health endpoint does not
  connect to or check the database.
- **Contract and checks:** `app.export_openapi` exports the FastAPI schema;
  `openapi-typescript` generates mobile types from the snapshot. Backend tests
  cover the health response and snapshot consistency. CI also checks generated
  mobile types, typechecking, lint, formatting and an Android bundle export.

## Current trust boundaries

The mobile app and any API caller are outside the backend trust boundary.
The health endpoint is public and returns only a fixed status; there is no
authentication, authorization, user data or server-side user isolation yet.
The generated types do not authenticate callers or validate network data.
Local HTTP and Compose credentials are for development, not a production
security configuration. No production transport, deployment or encryption
configuration is implemented here.

## Planned target and invariants

The following are requirements for future work, **not implemented features**:

```text
Mobile app -> HTTPS/JSON -> FastAPI -> PostgreSQL
                               |
                               -> Open Food Facts adapter and server cache
```

- Authenticate users and derive identity from validated credentials, never
  from a request body or another client-controlled user ID. Enforce ownership
  on the server for all reads and writes of user-owned records. Custom foods
  remain private to their owner; no family or sharing access is planned.
- Store calorie and nutrient snapshots on diary entries. They must remain
  unchanged when the source food is corrected or changed, preserving historical
  totals. Test both snapshot preservation and cross-user isolation.
- Use OpenAPI as the contract across backend and mobile. Validate untrusted
  input at boundaries, handle failures explicitly, and keep generated
  artifacts and consumers synchronized.
- Minimize health-adjacent data collection and logging. Plan HTTPS, appropriate
  encryption at rest, account deletion and export; do not commit secrets or
  real user data. Respect Open Food Facts attribution and licensing, and do not
  integrate BLS before its licensing is confirmed.
- Profile, diary, food search, barcode scanning and private foods are planned
  for the MVP. Local SQLite caching and offline synchronization, recipes,
  statistics, AI recognition and wearables are later plans, not current
  capabilities.

## Open decisions

As recorded in the [specification](./PROJECT_SPEC.md#quality-privacy-and-open-decisions),
the final mobile platform choice, authentication approach, hosting and budget,
optional web support, BLS licensing, and name and branding remain open. Expo
and FastAPI are present in the scaffold; that does not settle the remaining
product and deployment decisions.
