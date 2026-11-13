# Phase 1 plan: mobile MVP

This is an implementation plan, not a description of shipped functionality.
The [project specification](./PROJECT_SPEC.md) defines the product scope; the
[architecture overview](./architecture.md) describes the Phase 0 foundation.
Today there is only a placeholder mobile screen, a health endpoint, a local
PostgreSQL service, an empty Alembic environment and an OpenAPI type-generation
pipeline. No authentication, user data or food integration exists yet.

## Outcome and boundaries

**M1:** family members, each using a separate private account, can search for
or scan a food, log it in a meal and see daily totals. There is no family
account, sharing or access to another person's information. The complete MVP
also includes account lifecycle, profile and goals, diary editing, private
custom foods and a limited iOS/Android beta.

Recipes, weight history, water, favorites, full offline use and sync, statistics,
AI recognition, wearables and BLS integration are outside this phase. A current
weight in the profile is needed for goals; it is not weight history. The MVP
is online-only and must clearly report network failures rather than pretending
to save offline.

## Order, dependencies and estimates

Estimates are rough engineering hours including implementation, tests, review
and documentation, not calendar days. With one part-time developer, 118–171
hours at 10–15 hours/week is roughly 8–17 weeks, excluding external review
delays. The specification's 6–8 weeks is an optimistic target, not a
commitment; device testing, store review and unfamiliar tools may extend it.

| Step | Deliverable | Depends on | Estimate |
| --- | --- | --- | --- |
| 0 | Resolve blocking decisions and test foundation | Phase 0 | 8–12 h |
| 1 | Accounts, sessions and deletion | 0 | 18–26 h |
| 2 | Profile and goals | 1 | 12–18 h |
| 3 | OFF search, barcode lookup and cache | 0, 1 | 18–26 h |
| 4 | Private custom foods | 1, 3 | 12–18 h |
| 5 | Diary, snapshots and totals | 1, 2, 3, 4 | 20–28 h |
| 6 | Mobile search, scanning and logging flow | 2, 3, 4, 5 | 18–25 h |
| 7 | Security review and family beta | 1–6 | 12–18 h |

Each step ends with its acceptance checks passing and can be reviewed
independently. Steps 2 and 3 can proceed in parallel after step 1 if capacity
allows; the estimates assume one developer. Narrow API slices may be merged
incrementally, but no step is considered complete until its specified backend
and mobile behavior and tests pass.

## Shared design and test rules

The endpoints and tables below are proposed contract shapes, not existing
APIs. Finalize exact schemas, units and status codes in OpenAPI before
implementation; version or otherwise communicate breaking changes. Validate
all inputs server-side, return stable error codes with safe messages, and
never leak tokens, passwords, health data or stack traces in logs or errors.
Use HTTPS outside local development and reject unsafe production settings.

Every private read, update and delete must derive the user from a validated
session and scope the database operation to that user, including referenced
foods and entries. Never accept an authoritative `user_id` from the client.
Use database constraints and transactions as well as application checks; do
not rely on mobile filtering. A nonexistent resource and another user's
private resource should be indistinguishable to the caller.

Use TDD where practical: first demonstrate the intended failing test, then
implement and refactor. Backend integration tests use a migrated test
PostgreSQL database, two separate users and fake OFF responses; never use real
health data. Add a suitable mobile test runner when mobile behavior is
introduced, with component tests for user-visible flows and mocked network and
camera boundaries. The current scaffold does not have one. Test failure and
permission states as well as success.

For each API change, update backend schema and tests, regenerate and commit
`backend/openapi.json` and `mobile/src/api/schema.d.ts`, update affected
mobile consumers and tests, and run the checks in the
[README](../README.md#checks-and-api-contract). Generated TypeScript types do
not validate responses at runtime. Review migrations, test migration from an
empty database and document deployment and rollback; never treat dropping
production data as an acceptable rollback.

## 0. Decisions and test foundation

- Choose the authentication and hosting approach, security settings and beta
  infrastructure before account work; compare alternatives below rather than
  treating a recommendation as decided. Set up isolated test PostgreSQL,
  migration fixtures and deterministic OFF fakes.
- Decide the product policy for plausible nutrient ranges, missing nutrients,
  rounding, date/time-zone handling and goal limits before dependent schemas.
  Record those choices and test vectors. Define a safe user-visible error
  format and mobile runtime response-validation strategy.
- **Acceptance:** a fresh test database migrates successfully; the backend
  can exercise two isolated test identities without external services.
  Blocking decisions are recorded with their owner and implications.

## 1. Accounts, sessions and deletion

- Provide registration and login, short-lived access credentials, refresh,
  logout/revocation and confirmed account deletion. Proposed API:
  `POST /auth/register`, `/auth/login`, `/auth/refresh`, `/auth/logout`, and
  `DELETE /account`. These paths are subject to the auth-provider decision.
- Store password hashes using a vetted password-hashing implementation, never
  plaintext. Validate credentials and expiry server-side; rotate or otherwise
  revoke refresh credentials on logout, reuse or deletion. Store mobile
  credentials in platform-protected secure storage, not logs or ordinary
  preferences. Use generic login failures and rate limiting; document email
  normalization, password policy and session-expiry UX.
- Model a user and revocable refresh sessions, or map the external provider's
  subject to an internal user. Deletion must revoke sessions and remove all
  user-owned profile, private food and diary data, including applicable
  external identity records; shared OFF cache is not user-owned. Define
  backup retention and deletion from backups in the deployment policy, and
  tell users about the retention period.
- **Tests and acceptance:** registration, duplicate/invalid credentials,
  login, refresh rotation/expiry/reuse, logout, and deleted-account tokens
  behave as documented. A deletion transaction removes owned data and leaves
  other users and shared data intact. Mobile shows errors and signs out after
  deletion; no user-controlled ID grants access.

## 2. Profile and goals

- Proposed `GET`/`PUT /profile` and `GET`/`PUT /goals` operate only on the
  authenticated user's profile. Store birth date rather than a stale age,
  current weight, height, sex used by the calculation, activity, goal and
  editable calorie and macro targets. Avoid collecting extra health data.
- Calculate age from the selected date, apply Mifflin–St Jeor and the chosen
  activity/goal factors, and apply documented sensible bounds. Present the
  result as an estimate, allow edits and display the no-medical-advice notice.
  Agree on units, rounding and options before finalizing the schema; never
  silently substitute a sex or activity value.
- **Tests and acceptance:** calculation reference vectors, boundaries, invalid
  or missing profile inputs, editable overrides and persistence are covered.
  A second user cannot read or modify the profile or goals. The mobile form
  explains validation and makes the disclaimer visible.

## 3. OFF search, barcode lookup and cache

- Implement a replaceable server-side OFF adapter and a shared product cache.
  Proposed `GET /foods/search?q=...` and `GET /foods/barcode/{barcode}` return
  normalized products and source/attribution information. Set an appropriate
  identifying user agent, respect OFF's current usage limits and terms, and
  use bounded timeouts and explicit upstream error handling.
- Cache by stable external ID/barcode, record retrieval time and source,
  define refresh/expiry behavior and avoid duplicate cache rows. Normalize
  units to nutrients per 100 g; distinguish missing values from zero. Mark
  incomplete or implausible data and do not silently invent nutrients. Handle
  duplicates and allow the user to create a private corrected copy without
  changing shared source data or existing diary snapshots.
- Display source and attribution in product UI and ship any required ODbL
  notices, links and obligations after checking the current OFF terms for the
  actual data use. Confirm BLS licensing separately **before** any BLS data is
  integrated; it is not a Phase 1 dependency.
- **Tests and acceptance:** mocked search, barcode match/not-found, duplicate,
  missing/malformed nutrients, unit conversions, cache hit/refresh, timeouts,
  rate-limit and OFF outage have deterministic results. Unavailable data is
  clearly reported, not represented as a successful empty or zero result.

## 4. Private custom foods

- Proposed `POST /foods/custom`, `GET /foods/custom`, and
  `GET`/`PATCH`/`DELETE /foods/custom/{id}` manage owner-scoped foods. Store
  owner, name, optional barcode/brand and validated nutrients per 100 g; a
  corrected OFF copy is a new private food with source provenance. Define
  whether optional nutrients may be unknown and show that state in the UI.
- Separate shared cache records from private records through constraints and
  query policy. Delete or edit a custom food without destroying existing diary
  snapshots; use a nullable reference or another explicitly tested strategy.
- **Tests and acceptance:** create, list, edit and delete work for the owner;
  another user cannot discover, use or mutate the food even by guessing its
  ID. Invalid units and implausible values are rejected or explicitly flagged
  under the agreed policy.

## 5. Diary, snapshots and totals

- Proposed `GET /diary?date=YYYY-MM-DD`, `POST /diary/entries`,
  `PATCH`/`DELETE /diary/entries/{id}` and `GET /diary/totals?date=...`.
  Persist owner, local diary date, meal (`breakfast`, `lunch`, `dinner`,
  `snack`), food reference/provenance, amount and serving unit/grams, and
  calorie and macro snapshots. Store actual entry nutrition and enough
  per-100-g/serving basis to support deterministic amount edits without
  consulting mutable food data.
- Treat snapshots as immutable with respect to later source-food changes.
  An explicit user edit of the amount recalculates from the entry's stored
  basis; replacing the food explicitly creates a new snapshot from the newly
  selected food. Define rounding and unknown-nutrient behavior consistently
  for entry, meal and day totals; do not imply an incomplete total is complete.
  Use the user's explicit diary date, not the server's local date.
- **Tests and acceptance:** create, list by date/meal, edit and delete; verify
  amount conversion, totals and progress against fixed vectors, empty days,
  dates around time-zone boundaries, missing nutrients and invalid amounts.
  Editing/deleting source foods or refreshing OFF cache never changes existing
  snapshots or totals. Another user cannot access or change entries or use
  another user's custom food, including through guessed IDs.

## 6. Mobile search, scanning and logging

- Implement accessible mobile flows for sign-in, profile, search, product
  details, portion selection, custom foods, meal diary and daily/meal progress.
  Route all data through the authenticated API; validate response shapes and
  show loading, validation, expired-session and network error states.
- Request camera permission only when scanning; handle denial and cancellation
  and provide manual barcode entry and text search as fallbacks. A scanned
  barcode uses the same server lookup and confirmation/portion flow as search.
  Test on both platforms; never store user data in logs or expose credentials.
- **Tests and acceptance:** mobile component tests cover search and scan
  success, unavailable product, permission denied, validation and API failure.
  On iOS and Android devices, a signed-in user can search or scan, confirm a
  portion, save it to a chosen meal and see correct meal and day totals.

## 7. Security review and family beta

- Provision an HTTPS backend and persistent PostgreSQL with restricted
  credentials, backups and documented restore/deletion procedures. Set
  platform-specific bundle IDs, signing and environment configuration; use
  TestFlight and Android internal testing. Keep beta distribution private and
  publish privacy, attribution, support and no-medical-advice information.
- Run backend/mobile checks and migration tests, verify installation and
  update on representative iOS and Android devices, and perform a two-user
  authorization and account-deletion review. Record beta defects and a rollback
  owner; do not enable sharing or imply medical accuracy.
- **M1 acceptance:** at least two family testers with separate accounts can
  register, set goals, search **and** scan representative products, log
  portions in a meal and see correct meal/day totals. Each is denied access
  to the other's profile, custom foods and diary. Deletion and session
  revocation work, private custom foods work, and all step acceptance tests and
  pull-request checks pass. Record device results and unresolved blockers
  before distributing the beta; M1 is not complete if scanning is untested.

## Decisions and risks to resolve

| Decision or risk | Options / consequence | Needed by |
| --- | --- | --- |
| Authentication | Own FastAPI credentials offer control but require secure password/session operations; Supabase Auth reduces auth implementation but adds provider dependency and external account deletion. Choose and document threat model and token lifecycle. | Step 0, before 1 |
| Hosting and costs | Managed hosting reduces operations but costs more; a VPS gives control but requires patching, backups and recovery. Confirm budget, HTTPS, secrets, database access and backup/deletion retention. | Step 0, before 1 and beta |
| Platform | Expo scaffold is available; confirm Expo/EAS, camera support, iOS signing and Android distribution. Alternatives require migration effort. | Step 0, before 6 |
| Nutrition quality | Choose accepted ranges, unknown-value UX, units, serving conversion and rounding; OFF coverage and inconsistent records may prevent accurate totals. Do not equate missing with zero. | Step 0, before 2–5 |
| Dates and goals | Decide diary time-zone/date policy, age reference date, calculation bounds and macro target defaults. Explain estimates and avoid medical claims. | Step 0, before 2 and 5 |
| OFF and BLS rights | Verify current OFF attribution, ODbL obligations, rate limits and data-use terms before release; BLS rights remain unresolved and integration is blocked until confirmed. | Step 3; BLS before any integration |
| Deletion and privacy | Decide provider deletion and backup retention, encryption at rest, logging and export policy. MVP account deletion removes active user data; export is planned for a later phase, not silently promised in MVP. | Step 1 and before beta |
| Beta availability | Apple enrollment/review, iOS build access, Android tester setup and real devices can delay delivery; confirm owners and availability early. | Step 0, before 7 |

Record final decisions and any changes to scope in the specification and
architecture/development documentation when they are made. Do not mark planned
work as implemented until its acceptance checks pass.
