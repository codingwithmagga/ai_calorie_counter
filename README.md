# NutriLog

NutriLog is a mobile-first calorie and nutrition tracker for individual accounts. This repository currently contains a Phase 0 foundation, **not** the MVP. See the [architecture overview](docs/architecture.md) for implemented and planned boundaries, and the [project specification](docs/PROJECT_SPEC.md) for scope, roadmap and open decisions.

## Prerequisites

Python 3.12, Node.js 22, Docker Compose, and an iOS/Android simulator or Expo Go. Native iOS builds require macOS or EAS.

## Local development

From the repository root:

```sh
docker compose up -d
python3 -m venv .venv
. .venv/bin/activate
pip install -r backend/requirements-dev.txt
cd backend
export DB_PASSWORD=localdev
export DATABASE_URL="postgresql+psycopg://nutrilog:${DB_PASSWORD}@localhost:5432/nutrilog"
alembic upgrade head
uvicorn app.main:app --reload
```

The database credentials above are **local development only**. Never use them in production. The API is at `http://localhost:8000`, with interactive documentation at `/docs` and a health endpoint at `/health`.

In another terminal:

```sh
cd mobile
npm ci
npm start
```

Follow Expo's instructions to launch on a device or simulator. The screen is a placeholder, not a connected diary.

## Checks and API contract

```sh
cd backend
ruff check .
ruff format --check .
pytest
python -m app.export_openapi
cd ../mobile
npm run generate-api
npm run typecheck
npm run lint
npm run format:check
```

Regenerate and commit `backend/openapi.json` and `mobile/src/api/schema.d.ts` whenever the API changes. The mobile app uses `openapi-fetch` with these generated types. See [development notes](docs/development.md) for migration and build details.
