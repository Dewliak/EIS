# EU Data Compass web app (Streamlit prototype)

Portugal-hosted instance of the EU Data Compass mobility platform. Origin is fixed to
Portugal; the user picks a destination, an intent (traveling / moving), and a
subject, then lands in the **Deadlines · Documents · Information** dashboard.

Access to the whole app is **gated by the EUDI Wallet verifier** — the Streamlit
client shows a QR sign-in request and only the configured nationalities are let
in before any content renders.

> **Prototype, not the target.** The build target is the multi-page EU-portal
> app in [`../docs/01-plan/IMPLEMENTATION-PLAN.md`](../docs/01-plan/IMPLEMENTATION-PLAN.md)
> (spec: `../docs/02-spec/PLATFORM-SPEC.md`). This prototype covers the single
> dashboard + the Residence subject only.

## What's real vs mock

| Destination | Content | Source |
|---|---|---|
| 🇩🇪 Germany | **Verified** — primary worked case (PT → DE) | `docs/04-research/MOVING-CASE.md`, `DOCUMENTS-INDEX.md` |
| 🇪🇸 Spain | **Verified** — second case | `docs/04-research/SPAIN-VALIDATION.md` |
| SK, HU, SI, HR, RO, BG, GR, CY | **Rough / unverified** — badged in the UI | `docs/04-research/COUNTRY-MATRIX.md` |

Short-stay (traveling, < 3 months) content is real for **every** destination —
the universal EU freedom-of-movement baseline (`docs/04-research/TRAVELING-CASE.md`).

Only the **Residence & Registration** subject is live; other subjects are stubbed
"coming soon". The **Inform with ID** button and per-document **Sign** button are
wallet-gated stubs (disabled) — that layer lands ~2027 (`docs/02-spec/EUDI-WALLET.md`).

## Pieces

| Piece | What | Port |
|---|---|---|
| `../eudi_login/service.py` | **FastAPI** verifier (OpenID4VP, mocked). Issues the QR, polls, checks nationality. | 5000 |
| `../eudi_login/client.py` | Streamlit login widget the app calls to gate access. | — |
| `app.py` | The mobility dashboard, gated by the client above. | 8501 |
| `data.py` | Content dataset (no invented facts; sourced from `../docs`). | — |
| `../login_app.py` | Standalone login demo (optional; the dashboard already gates itself). | — |

## Run — see [`../readme.md`](../readme.md#launch) for the full launch guide

Short version (two processes):

```bash
python3 -m venv .venv
.venv/bin/pip install -r ../requirements.txt

# Terminal 1 — verifier service.
# PUBLIC_BASE_URL must be a public HTTPS URL (e.g. a tunnel) for a real wallet
# to POST its callback; localhost is fine to see the flow with the sandbox.
PUBLIC_BASE_URL=https://your-tunnel.example.com \
  .venv/bin/uvicorn eudi_login.service:app --host 0.0.0.0 --port 5000

# Terminal 2 — the gated EU Data Compass site.
EUDI_API_URL=http://localhost:5000 \
ALLOWED_NATIONALITIES=PT,DE,FR,NL,IT,ES,SK \
  .venv/bin/streamlit run webapp/app.py --server.port 8501
```

Open **http://localhost:8501**. The QR uses SVG (no Pillow dependency).

> Prototype verifier: no production-grade signature, trust-chain, key-binding,
> nonce/audience, or revocation validation.
