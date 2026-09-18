# 07 — Emergency Alert Demo (what's actually implemented)

This document describes the **first working slice** of the emergency layer: the backend API in
`eudi_login/service.py` and the two Flutter apps in `mobile/`. It is deliberately narrow — one
backend, one destination country's authority, one home country's citizens — as a proof of concept
for **leg 3** of [`12-EMERGENCY-ROUTING-PROPOSAL.md`](../12-EMERGENCY-ROUTING-PROPOSAL.md) ("home
country → its own citizens"). It does **not** implement country-to-country routing (legs 1–2 of
that proposal) — see [Relation to the routing proposal](#relation-to-the-routing-proposal) below.

## Actors

- **Citizen app** (`mobile/citizen_app`) — a Portuguese traveller registers a trip to Germany,
  receives alerts matched to that trip, and can acknowledge, mark themselves safe or needing help,
  and (with explicit, per-emergency consent) send one location check-in per day.
- **Authority app** (`mobile/authority_app`) — a single-screen demo for a German emergency
  authority: simulate a hazard, review it, publish an alert. No login screen; it opens a demo
  session automatically.
- **Backend** (`eudi_login/service.py`) — one FastAPI service, one SQLite database (`eis.db`),
  shared by both apps and by the web app's wallet-login endpoints.

## Auth model (important limitation)

The mobile apps do **not** use the EUDI wallet login the web app uses. They call
`POST /api/demo/citizen/session` or `POST /api/demo/authority/session`, which mints a random
bearer token tied to a **hard-coded demo user** (`demo-citizen-pt-001` / `demo-authority-de-001`) —
see `_demo_session()` in `eudi_login/service.py`. Every citizen-app install is the same demo
citizen; every authority-app install is the same demo authority. This is fine for a single-device
demo and wrong for anything real. Wiring the mobile apps into the actual wallet-login flow
(`/login` → QR → `/callback` → `/status/{state}`, the same flow `eudi_login/client.py` uses) is
unbuilt.

## Data model (SQLite tables)

| Table | Purpose |
|---|---|
| `travel_registrations` | A citizen's trip: origin (always `PT` today), destination country/region, dates, phone, push opt-in. Created by "Inform with ID" on the web app or the citizen app's inform screen. |
| `devices` | FCM token per citizen device. Stored but unused — see [What's mocked](#whats-mocked). |
| `hazards` | A detected hazard. `provider`/`satellite_status` are always `"simulated"` in this slice. |
| `alerts` | An authority-authored alert, optionally linked to a hazard. Lifecycle: `draft` → `published` → `closed`. |
| `alert_recipients` | Join table: which registration was matched to which alert, its delivery/citizen status. |
| `location_consents` | Per-alert, per-citizen opt-in to share location. Expires with the alert (`valid_until`). |
| `location_checkins` | One row per location share. Rate-limited to one per 24h per (alert, citizen) pair. |
| `audit_events` | Append-only log of who did what, for every state-changing endpoint. |

## API reference

All emergency endpoints require `Authorization: Bearer <demo token>` from the matching
`/api/demo/{citizen,authority}/session` call.

### Citizen

| Endpoint | What it does |
|---|---|
| `POST /api/citizen/registrations` | Create a travel registration (destination, dates, phone, push opt-in). Origin is hard-coded `PT`. |
| `POST /api/devices` | Register an FCM token for the device (accepted but not yet used to send real push). |
| `GET /api/citizen/alerts` | List alerts matched to this citizen's registrations, most recent first. |
| `POST /api/citizen/alerts/{id}/{action}` | `action` is one of `acknowledge`, `safe`, `help`. Records the citizen's status on the alert. |
| `POST /api/citizen/alerts/{id}/location-consent` | Opt in to sharing location for this specific alert. Consent expires when the alert's `valid_until` passes. |
| `DELETE /api/citizen/alerts/{id}/location-consent` | Revoke consent. |
| `POST /api/citizen/alerts/{id}/location-checkins` | Submit one location point. Requires active consent; rejected with `429` if one was already submitted in the last 24h. |

### Authority

| Endpoint | What it does |
|---|---|
| `POST /api/authority/hazards/simulate` | Create a hazard with `satellite_status="simulated"`. Defaults to a flood in Berlin, 92% confidence. |
| `GET /api/authority/hazards` | List hazards. |
| `POST /api/authority/hazards/{id}/review` | Mark a hazard reviewed by a human before it can back an alert. |
| `POST /api/authority/alerts` | Draft an alert (title, body, instructions, affected country/region, validity window, source URL). Matches it against active `travel_registrations` for the affected region and creates `alert_recipients` rows. |
| `GET /api/authority/alerts` | List alerts issued by this authority. |
| `POST /api/authority/alerts/{id}/publish` | Move an alert from `draft` to `published` — this is the point at which citizens can see it via `GET /api/citizen/alerts`. |
| `POST /api/authority/alerts/{id}/close` | Close an alert (ends the emergency; location consent tied to it also lapses). |

### Wallet login (shared with the web app)

| Endpoint | What it does |
|---|---|
| `GET /health` | Liveness check. |
| `POST /login` | Start an OpenID4VP transaction; returns a QR code + sandbox link. |
| `POST /callback` | The EUDI wallet posts its verified response here. |
| `GET /status/{state}` | Polled by the client to learn `pending` / `verified` / `rejected`. |

## What's mocked

- **Satellite detection** — `POST /api/authority/hazards/simulate` fabricates a hazard; there is no
  Copernicus (or any other) data ingestion.
- **Push delivery** — `devices` stores FCM tokens, but nothing in this repo calls Firebase Cloud
  Messaging or APNs. The citizen app only sees new alerts while it is open (via mock data or
  polling `GET /api/citizen/alerts` against a real backend) and shows a **local** device
  notification, not a push from a server.
- **Identity** — the demo bearer tokens are not derived from a wallet-verified identity at all;
  see [Auth model](#auth-model-important-limitation) above.
- **Persistence** — a single SQLite file, no migrations, no backups. In-memory `DEMO_SESSIONS` are
  lost on every backend restart, which logs every demo user out.

## Relation to the routing proposal

[`12-EMERGENCY-ROUTING-PROPOSAL.md`](../12-EMERGENCY-ROUTING-PROPOSAL.md) proposes a 3-leg,
country-to-country architecture: destination country detects + publishes (leg 1), destination and
home country's platform nodes exchange the alert over eDelivery/AS4 (leg 2), and the home country
relays it to its own citizens (leg 3) — so that no citizen's personal data ever crosses a border.

This demo implements **only leg 3, collapsed into a single backend**: there is one database, one
"authority," and one "citizen," so there is no country boundary to cross yet. Building legs 1–2
(a second backend representing a second country, and a transport between them) is unbuilt; the
proposal document's open questions (§8) are the starting point for that work.

## Mobile app details

See [`mobile/README.md`](../../mobile/README.md) for how to run the apps (standalone with mock
data, or against a real backend) and [`mobile/citizen_app/README.md`](../../mobile/citizen_app/README.md) /
[`mobile/authority_app/README.md`](../../mobile/authority_app/README.md) for what each app screen
does.
