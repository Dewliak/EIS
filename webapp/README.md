# EIS web app (Streamlit prototype)

Portugal-hosted instance of the EIS mobility platform. Origin is fixed to
Portugal; the user picks a destination, an intent (traveling / moving), and a
subject, then lands in the **Deadlines · Documents · Information** dashboard.

> **Prototype, not the target.** The build target is the multi-page EU-portal
> app specified in [`../docs/01-plan/IMPLEMENTATION-PLAN.md`](../docs/01-plan/IMPLEMENTATION-PLAN.md)
> (see `../docs/02-spec/PLATFORM-SPEC.md` and `../docs/02-spec/PLATFORM-CONCEPT.md`).
> This prototype covers the single dashboard + Residence subject only.

## What's real vs mock

| Destination | Content | Source |
|---|---|---|
| 🇩🇪 Germany | **Verified** — primary worked case (PT → DE) | `docs/04-research/MOVING-CASE.md`, `DOCUMENTS-INDEX.md` |
| 🇪🇸 Spain | **Verified** — second case | `docs/04-research/SPAIN-VALIDATION.md` |
| SK, HU, SI, HR, RO, BG, GR, CY | **Rough / unverified** — badged in the UI | `docs/04-research/COUNTRY-MATRIX.md` |

Short-stay (traveling, < 3 months) content is real for **every** destination —
it's the universal EU freedom-of-movement baseline (`docs/04-research/TRAVELING-CASE.md`).

Only the **Residence & Registration** subject is live; other subjects are stubbed
"coming soon". The **Inform with ID** button and per-document **Sign** button are
wallet-gated stubs (disabled) — the EUDI Wallet layer lands ~2027
(`docs/02-spec/EUDI-WALLET.md`).

## EUDI Wallet verifier (separate)

The wallet login lives outside this app:

- `../eudi_login/service.py` — **FastAPI** verifier service (OpenID4VP, mocked verification). Runs on port 5000.
- `../eudi_login/client.py` — Streamlit-side login widget that POSTs to the service and polls status.
- `../login_app.py` — Streamlit demo app gated by `EUDIWalletLogin`.

## Files

- `app.py` — Streamlit UI (navigation + dashboard).
- `data.py` — content dataset (no invented facts; sourced from `../docs`).

## Run

```bash
python3 -m venv .venv
.venv/bin/pip install -r ../requirements.txt
.venv/bin/streamlit run webapp/app.py
```

Then open http://localhost:8501 (Streamlit's default port).
