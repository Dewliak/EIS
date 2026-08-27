# EIS — European Impact Sprints

Unified European mobility platform + EU Digital Identity Wallet identity/emergency layer.

> **Worked example:** Portuguese citizens → Germany (Berlin). Third-country validation: Spain.

## The project

Two parts, one repo:

| Part | Where | What |
|---|---|---|
| **Code** | `login_app.py`, `eudi_login/`, `webapp/` | EUDI Wallet OpenID4VP verifier + Streamlit web prototype |
| **Research & spec** | `docs/` | Full platform spec, subcategory cases, sources, PDF forms |

## Start here

1. **`docs/01-plan/IMPLEMENTATION-PLAN.md`** — the master build plan (site map, pages, flows,
   doc map). Hand this to whoever builds the site.
2. **`docs/README.md`** — index of every document.

## Code

- **`login_app.py` + `eudi_login/`** — EUDI Wallet OpenID4VP verifier (Flask prototype). Routes:
  `/login`, `/qr`, `/callback`, `/status/<id>`, `/result/<id>`, gated by nationality
  (`ALLOWED_NATIONALITIES`). **⚠️ PROTOTYPE** — signature/trust-chain verification, key-binding,
  revocation, replay protection, signed request objects are all mocked.
- **`webapp/`** — Streamlit web prototype (sibling-built).

### Run the verifier

```bash
pip install -r requirements.txt
cloudflared tunnel --url http://localhost:5000   # or: ngrok http 5000
PUBLIC_BASE_URL=https://your-tunnel.example.com python login_app.py
```

Test against the sandbox **eudi-test.dev** (needs https to reach `/callback`).

## Documentation — `docs/`

```
docs/
├── 01-plan/IMPLEMENTATION-PLAN.md   # master build plan (start here)
├── 02-spec/                         # PLATFORM-SPEC, PLATFORM-CONCEPT, EUDI-WALLET
├── 03-cases/                        # SUBCATEGORIES + cases/ (7 subcategory docs)
├── 04-research/                     # personas, cases, documents index, country matrix
├── 05-resources/                    # sources, PDF URLs, assisting platforms
├── 12-EMERGENCY-ROUTING-PROPOSAL.md # emergency routing proposal (sibling-authored)
└── assets/pdf/                      # fetched forms (3 PDFs)
```

## Key verified facts

- **Travel <3 months:** valid ID only — no visa, no residence permit, no registration.
- **Move >3 months (Germany):** Anmeldung at Bürgeramt within **14 days** (fine up to €1,000);
  landlord confirmation required (lease alone isn't enough).
- **Deadline clocks differ per country:** DE 14 days · PT 30 days after month 3 · ES within 3 months.
- **EUDI Wallet:** ≥1 wallet per member state by **24 Dec 2026** (Regulation (EU) 2024/1183).

See `docs/01-plan/IMPLEMENTATION-PLAN.md` and `docs/README.md`.
