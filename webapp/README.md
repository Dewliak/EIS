# EIS web app (Streamlit)

Portugal-hosted instance of the EIS mobility platform. Origin is fixed to
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

Only the **Residence & Registration** subject is live; other subjects are stubbed
"coming soon". The **Inform with ID** button and per-document **Sign** button are
wallet-gated stubs (disabled) — the EUDI Wallet layer lands ~2027 (`docs/09` §6.2).

Access to the site itself is protected by the EUDI Wallet verifier in
`../eudi_login/`. The Streamlit client shows its QR request before any EIS content
is rendered and permits only the configured nationalities.

## Files

- `app.py` — Streamlit UI (navigation + dashboard).
- `data.py` — content dataset (no invented facts; sourced from `../docs`).

## Run

```bash
python3 -m venv .venv
.venv/bin/pip install -r ../requirements.txt
# Terminal 1: wallet verifier. PUBLIC_BASE_URL must be a public HTTPS URL
# (for example a tunnel URL) that the wallet can POST its callback to.
PUBLIC_BASE_URL=https://your-tunnel.example.com \
  .venv/bin/uvicorn eudi_login.service:app --host 0.0.0.0 --port 5000

# Terminal 2: protected EIS site.
EUDI_API_URL=http://localhost:5000 \
ALLOWED_NATIONALITIES=PT,DE,FR,NL,IT,ES,SK \
  .venv/bin/streamlit run webapp/app.py
```

Then open http://localhost:8501 (Streamlit's default port).

This remains a prototype verifier: it does not yet perform production-grade
signature, trust-chain, key-binding, nonce/audience, or revocation validation.
