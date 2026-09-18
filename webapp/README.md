# EU Data Compass web app (Streamlit prototype)

Part of the [EIS monorepo](../readme.md). Portugal-hosted instance of the EU Data Compass mobility
platform. Origin is fixed to Portugal; the user picks a destination, an intent (traveling /
moving), and a subject, then lands in the **Deadlines · Documents · Information · Data & privacy**
dashboard.

Access to the whole app is **gated by the EUDI Wallet verifier** — the Streamlit
client shows a QR sign-in request and only the configured nationalities are let
in before any content renders.

> **Prototype, not the target.** The build target is the multi-page EU-portal
> app in [`../docs/01-plan/IMPLEMENTATION-PLAN.md`](../docs/01-plan/IMPLEMENTATION-PLAN.md)
> (spec: `../docs/02-spec/PLATFORM-SPEC.md`). This prototype covers a single dashboard page.

## What's real vs mock

| Destination | Content | Source |
|---|---|---|
| 🇩🇪 Germany | **Verified** — all 8 subjects (Residence, Work, Studies, Tax, Health, Social security, Vehicle, Family), for both traveling and moving in | `../docs/04-research/`, `../docs/06-subjects/` |
| 🇪🇸 Spain | **Verified** — moving-in case | `../docs/04-research/SPAIN-VALIDATION.md` |
| SK, HU, SI, HR, RO, BG, GR, CY | **Rough / unverified** — badged in the UI | `../docs/04-research/COUNTRY-MATRIX.md` |
| Everyone else | Universal short-stay (< 3 months) baseline only | `../docs/04-research/TRAVELING-CASE.md` |

All 8 subject buttons are clickable for every country; non-Germany/Spain destinations show "No
content available for this combination yet" outside the short-stay baseline.

**Inform with ID** is a full working prototype flow (draft → review → "approve with EU Wallet
(demo)"), not a stub — it stores the notification in the browser session and explains retention in
the Data & privacy tab. Each document card's **Sign with wallet** button opens a mock signing
dialog that returns a downloadable demo PDF. Neither is a real EUDI Wallet transaction — both are
demo/mock flows layered on top of the real wallet-login gate that protects the whole app.

There's also a **"Try the Berlin conference demo"** shortcut on the destination-picker screen: a
dedicated short-stay business-travel scenario for Germany (`webapp/data.py:_germany_traveling`),
separate from the regular Germany content.

## Pieces

| Piece | What | Port |
|---|---|---|
| `../eudi_login/service.py` | **FastAPI** verifier (OpenID4VP, mocked). Issues the QR, polls, checks nationality — also hosts the mobile apps' emergency-alert API, see [`../docs/07-emergency/EMERGENCY-DEMO.md`](../docs/07-emergency/EMERGENCY-DEMO.md). | 5000 |
| `../eudi_login/client.py` | Streamlit login widget the app calls to gate access. | — |
| `app.py` | The mobility dashboard, gated by the client above. | 8501 |
| `data.py` | Content dataset (no invented facts; sourced from `../docs`). | — |
| `../login_app.py` | Standalone login demo (optional; the dashboard already gates itself). | — |

## Run — see [`../readme.md`](../readme.md#launch) for the full launch guide

## Run locally with Docker and cloudflared

Use two terminals. Start the tunnel first so its public URL is available
before the verifier generates a wallet request:

```bash
# Terminal 1: create the public HTTPS URL. Keep this running.
cloudflared tunnel --url http://127.0.0.1:8080
```

Copy the `https://...trycloudflare.com` URL printed by cloudflared into both
`PUBLIC_BASE_URL` and `EUDI_API_URL` in a local `.env` file:

```bash
cp .env.example .env
# edit PUBLIC_BASE_URL and EUDI_API_URL in .env

# Terminal 2: start the combined application with the tunnel URL configured.
docker compose up --build
```

Open the cloudflared URL in the browser. Both the Streamlit UI and the EUDI
Wallet callback are routed through the same HTTPS URL.

If the container was already running with `http://localhost:8080`, restart it
after editing `.env`:

```bash
docker compose down
docker compose up --build
```

Never use `http://localhost:8080` or `http://127.0.0.1:8080` as
`PUBLIC_BASE_URL`; those addresses are only reachable from your own machine.

## Deploy on Railway

Create a Railway service from this repository. Railway detects the `Dockerfile`
and provides the public HTTPS URL and `PORT` automatically. Set these variables
in the Railway service settings:

```text
PUBLIC_BASE_URL=https://<your-railway-domain>
EUDI_API_URL=https://<your-railway-domain>
ALLOWED_NATIONALITIES=PT,DE,FR,NL,IT,ES,SK
```

The service exposes `/health` for Railway health checks. Nginx routes `/login`,
`/callback`, `/status/*`, and `/health` to FastAPI, and all other paths to
Streamlit.

> Prototype verifier: no production-grade signature, trust-chain, key-binding,
> nonce/audience, or revocation validation.
