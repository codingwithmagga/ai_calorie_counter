# Project specification: NutriLog (working title)

This is the planning baseline, not a description of completed features. The stack is a recommendation, not a fixed mandate; explain advantages and disadvantages of alternatives. The developer is strong in C++, intermediate in Python, and has some React/TypeScript experience. Prefer pragmatic, well-documented standard tools suitable for a part-time project.

## Vision and scope

Build a calorie and nutrient tracker for everyday family use and as a portfolio project. It is inspired by the functionality of Yazio, not its name, logo or visual design. Each family member has a separate account; no one can access another user's data, and there are no family or sharing features. iOS and Android are primary; browser use is rare.

MVP: registration, login and account deletion; profile (height, weight, age, sex, activity and goal); daily diary with breakfast, lunch, dinner and snacks; food search and barcode scanning; calorie and macro totals per meal and day with a daily goal; private user-created foods.

Later: recipes, weight history, water, favorites/recent foods, offline use, statistics, AI photo recognition and wearables. Out of scope: social features, sharing, coaching, subscriptions and recreating Yazio's database.

## Food data strategy

- Use Open Food Facts (OFF) as the primary source for packaged and barcode products; respect its terms, ODbL and attribution requirements.
- Investigate the Bundeslebensmittelschlüssel (BLS) for basic unpackaged foods; only integrate after confirming licensing permits it.
- Custom foods are private to their owner. Cache retrieved products server-side to reduce latency and API load and support corrections.
- Missing or incorrect nutrients, duplicates and inconsistent units are risks. Validate data, including calorie/macro plausibility, and support local corrections without changing historical diary snapshots.

## Recommended stack and alternatives

| Layer | Recommendation |
| --- | --- |
| Mobile | React Native, Expo, TypeScript and Expo Router |
| Scanner / local data | `expo-camera` / `expo-sqlite` (offline foundation, full sync later) |
| State and forms | TanStack Query for server state, Zustand for UI state, React Hook Form and Zod for forms and validation |
| Charts | `victory-native` or `react-native-gifted-charts` |
| API / data | Python FastAPI, PostgreSQL, SQLAlchemy 2, Alembic |
| Authentication | Email/password with access and refresh JWTs, or Supabase Auth |
| Isolation | Server-enforced `user_id` filtering for every user-owned table; optional PostgreSQL row-level security |
| Hosting | Small VPS, Fly.io or Railway; managed or containerized PostgreSQL |
| Distribution / CI | EAS Build, TestFlight and Android internal testing; GitHub Actions for lint, tests and build |

Capacitor can reuse a web app but feels less native; a PWA has iOS camera/push limitations. Flutter is native but requires learning Dart. Supabase as a complete backend accelerates delivery but shows less custom backend work; Supabase Auth plus FastAPI is a possible hybrid. Expo Web is optional and not a priority. Add libraries as needed rather than assuming all proposed tools are already installed.

## Architecture principles

Target: Expo app → HTTPS/JSON FastAPI backend → PostgreSQL; the backend integrates OFF through an interchangeable adapter and server cache. Local SQLite is intended for caching and a later offline sync queue. The OpenAPI schema is the contract and the TypeScript client is generated from it.

```text
Expo app (local SQLite cache / future sync queue)
    -> HTTPS / JSON, generated OpenAPI client
FastAPI (auth, profile, diary, food endpoints, OFF adapter and cache)
    -> PostgreSQL
```

Derive user identity from a validated token, never a request body. Every query for private data must filter by that identity on the server. Account deletion must remove the user's data. These are future implementation requirements, not claims about the Phase 0 scaffold.

## Proposed data model

- `users`: id, email, password hash, creation time.
- `profiles`: user_id, birth date, sex, height, activity, goal, calorie and macro targets.
- `foods`: id, source (OFF/BLS/custom), external id, barcode, name, brand, nutrients per 100 g and optional owner_user_id (only for custom foods).
- `food_servings`: food_id, label and grams.
- `diary_entries`: user_id, date, meal enum, food, amount, serving unit and calorie/macro snapshots. Snapshots preserve history when food data changes.
- `weight_logs`: user_id, date and weight; `water_logs` and recipes/recipe items are later additions.

## Calculations

Use Mifflin–St Jeor for basal metabolic rate and multiply by activity factor for total daily energy expenditure. Apply a deficit or surplus according to the user's goal, with sensible bounds and a clear statement that the app is not medical advice. Provide editable default macro targets.

## Roadmap

### Phase 0: setup (approximately one week)

Monorepo, lint/format and CI; FastAPI, PostgreSQL via Compose and Alembic; Expo TypeScript app with Router; generate a TypeScript client from OpenAPI.

### Phase 1: MVP (approximately 6–8 weeks)

Authentication and account deletion; profile and goals; diary CRUD; OFF search/cache; barcode scanning; totals and progress; private custom foods; family test via TestFlight and Android internal testing. **M1:** family members can log meals by search or scan and see daily totals.

### Phase 2: expansion (approximately 4–8 weeks)

Favorites, recent foods, meal copying, recipes, weight charts, water, weekly/monthly statistics and local reminders. **M2:** everyday use without frustration, with food correction for data quality.

### Phase 3: robustness and polish

Offline-first SQLite and sync queue; JSON/CSV export and complete account deletion for GDPR; unit tests for calculations, API integration tests and selected E2E flows; monitoring, backups and error logging.

### Phase 4: optional features

AI meal photo recognition, Apple Health / Health Connect, widgets and optional Expo Web.

## Quality, privacy and open decisions

Show clean architecture and API design, end-to-end types, authentication and isolation, external API caching/error handling, an offline strategy, tests, CI/CD, deployment and documentation including an architecture diagram and screenshots.

Collect health-adjacent data sparingly; keep user data on the chosen backend, use HTTPS and encryption at rest where possible, and plan deletion and export. Respect OFF licensing/attribution, confirm BLS rights and avoid Yazio branding. The app must include a no-medical-advice notice.

Still to decide: confirm Expo versus Capacitor/Flutter; own FastAPI auth versus Supabase/hybrid; hosting and budget; optional web; BLS licensing; final name and branding.
