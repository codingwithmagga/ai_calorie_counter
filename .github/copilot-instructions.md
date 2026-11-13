# AI-assisted development

## Project context

- Read the [project specification](../docs/PROJECT_SPEC.md) for product scope
  and planned requirements, the [architecture overview](../docs/architecture.md)
  for implemented boundaries, and the [development notes](../docs/development.md)
  for commands. Planned features are not evidence of implemented behavior.
- Follow the scoped backend and mobile instructions in
  [instructions](./instructions/).

## Non-negotiable requirements for future features

- Enforce user isolation on the server for every user-owned resource. Derive
  identity from validated authentication, never from a client-supplied user ID.
  Custom foods are private to their owner; the client is not an authorization
  boundary. Authentication and user data are not implemented yet.
- Preserve immutable nutrition snapshots on diary entries when food data
  changes; do not calculate historical totals from mutable current food data.
  The diary and snapshots are not implemented yet.
- Treat OpenAPI as the API contract. For API changes, update and test the
  backend and affected mobile behavior, regenerate and commit both
  `backend/openapi.json` and `mobile/src/api/schema.d.ts`, and run the
  cross-stack checks in the [README](../README.md#checks-and-api-contract).
- Minimize collection and logging of health-adjacent data; never commit secrets
  or real user data. Plan for HTTPS, account deletion, and data export; do not
  claim these protections exist until implemented and verified.

## Working approach

- Inspect affected code and tests, preserve existing behavior unless a change
  is requested, and keep changes focused. For larger tasks, identify affected
  backend, mobile, API, test, and documentation surfaces and work in small,
  independently verifiable steps. Make assumptions explicit and clarify
  material ambiguities before implementing.
- For behavior changes, use test-driven development where practical: write or
  update a test, verify it fails for the intended reason, implement the change,
  then refactor with tests passing. For bug fixes, first reproduce the issue
  with a failing regression test and run relevant regression checks after the
  fix. For documentation-only changes, explain appropriate validation instead.
- Add focused unit tests for behavior and edge cases and integration tests for
  meaningful boundaries. Do not remove unit tests unless replacement tests
  preserve their behavior and edge-case coverage. Include cross-user access
  and snapshot preservation tests when those features are introduced. Run
  relevant checks from the [README](../README.md#checks-and-api-contract).
- Handle failures explicitly, validate untrusted data at boundaries, and do not
  hide errors behind broad catches or success-shaped defaults.
- Before adding dependencies, check existing dependencies and the standard
  library; prefer maintained packages and follow existing dependency management.
- Update the architecture, development notes, specification, or these
  instructions when a change makes them inaccurate. Keep implemented behavior
  distinct from plans and record unresolved decisions. Keep internal
  documentation and code comments in English.
- Review the final diff for unrelated changes and verify relevant phase
  acceptance criteria before starting later-phase work.

## Git workflow

- For each new feature or bug fix, fetch `origin/main` and create a
  task-specific branch from it, for example `feature/MJS/<task-name>`. Create
  the branch without tracking `origin/main`; preserve existing work and resolve
  conflicts rather than discarding changes.
- When pushing the feature branch, set its upstream to its own matching
  `origin/<branch-name>` (for example with
  `git push --set-upstream origin <branch-name>`), never to `origin/main`.
  Prepare a pull request; do not merge locally or push commits directly to
  `main`. The repository owner merges through GitHub after checks pass.
- CI runs on pull requests, not standalone pushes. Run relevant checks locally
  and do not assume a pull request alone guarantees they pass.
