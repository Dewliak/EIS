# EU Data Compass web app (Streamlit)

Portugal-hosted instance of the EU Data Compass mobility platform. Origin is fixed to
Portugal; the user picks a destination, an intent (traveling / moving), and a
subject, then lands in the **Deadlines · Documents · Information** dashboard
(the flow specified in `../docs/00-PLATFORM-CONCEPT.md` and `../docs/09-FULL-PLATFORM-SPEC.md`).

## What's real vs mock

| Destination | Content |
|---|---|
| 🇩🇪 Germany | **Verified** — the primary worked case (Portugal → Germany), from `docs/02–04`. |
| 🇪🇸 Spain | **Verified** — second case, from `docs/10`. |
| SK, HU, SI, HR, RO, BG, GR, CY | **Rough / unverified** draft data from the `docs/11` registration matrix — badged in the UI. |

Short-stay (traveling, < 3 months) content is real for **every** destination —
it's the universal EU freedom-of-movement baseline.

Germany now includes sourced guides for Residence & Registration, Work, Studies,
Tax, Health, Social security, Vehicle and Family. Other country/subject
combinations may still be unavailable. The **Inform with ID** button and per-document **Sign** button are
wallet-gated stubs (disabled) — the EUDI Wallet layer lands ~2027 (`docs/09` §6.2).

Access to the site itself is protected by the EUDI Wallet verifier in
`../eudi_login/`. The Streamlit client shows its QR request before any EU Data Compass content
is rendered and permits only the configured nationalities.

## Files

- `app.py` — Streamlit UI (navigation + dashboard).
- `data.py` — content dataset (no invented facts; sourced from `../docs`).

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

This remains a prototype verifier: it does not yet perform production-grade
signature, trust-chain, key-binding, nonce/audience, or revocation validation.
