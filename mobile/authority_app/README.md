# eu_data_compass_authority

The **authority** side of the EU Compass emergency-alert demo (Flutter, Android-first). Part of the
[EIS monorepo](../../readme.md) — see [`mobile/README.md`](../README.md) for how to run it and
[`docs/07-emergency/EMERGENCY-DEMO.md`](../../docs/07-emergency/EMERGENCY-DEMO.md) for what the
demo actually implements versus what's mocked.

## What this app does

A single screen (`lib/main.dart`, `AuthorityHome`) — "Emergency control room". One button,
**"Simulate, review and publish alert"**, walks through the full authority side of the demo flow in
one tap:

1. Opens a demo authority session (`POST /api/demo/authority/session`).
2. Simulates a hazard (`POST /api/authority/hazards/simulate`) — a flood near Berlin with
   `satellite_status = "simulated"`.
3. Reviews the hazard (`POST /api/authority/hazards/{id}/review`).
4. Drafts an alert with the title from the text field (`POST /api/authority/alerts`).
5. Publishes it (`POST /api/authority/alerts/{id}/publish`) — this is the point where matching
   citizen registrations become recipients and the citizen app can see the alert.

With `USE_MOCK=true` (the default), all of this is simulated locally with a short delay instead of
calling the backend — see [Run](#run).

## Limitation: no real detection, no real authentication

There is no Copernicus (or any other) satellite feed behind "Simulate" — it fabricates a hazard.
There is no login screen; the app authenticates as a fixed demo authority id, the same for every
install. See [`docs/07-emergency/EMERGENCY-DEMO.md`](../../docs/07-emergency/EMERGENCY-DEMO.md) for
the full list of what's mocked in this slice.

## Run

See [`mobile/README.md`](../README.md) for both run modes (standalone with mock data, or against a
real backend). Generic Flutter tooling links: [Flutter docs](https://docs.flutter.dev/).
