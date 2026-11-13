---
description: "Use when changing the Expo React Native app, TypeScript, mobile API client, or mobile configuration."
applyTo: "mobile/**"
---

# Mobile guidance

- Follow the existing Expo Router, React Native and TypeScript patterns. Keep
  components focused, use explicit types at boundaries, and avoid unnecessary
  state and speculative abstractions.
- Keep HTTP concerns in the API client where practical. The generated OpenAPI
  types provide compile-time checking, not runtime validation; treat response
  payloads as untrusted and validate their runtime shape before use. Handle
  network, API and malformed-response errors explicitly where data is consumed.
- Do not rely on client-side filtering to protect user data. Authentication,
  diary, offline storage and food integrations are planned, not implemented.
- From `mobile/`, run `npm run typecheck`, `npm run lint`, and
  `npm run format:check` for relevant changes. CI also runs
  `npx expo export --platform android` as a bundle smoke check; no mobile
  test runner is currently configured.
- For API changes, update affected UI/client behavior and backend tests,
  regenerate both contract files, and run backend and mobile checks as
  described in the [README](../../README.md#checks-and-api-contract).
- Update relevant documentation and instructions when behavior, commands, or
  architecture changes.
