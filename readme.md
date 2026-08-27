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

## Code — architecture

| Piece | Tech | Role | Port |
|---|---|---|---|
| `eudi_login/service.py` | **FastAPI** | EUDI Wallet OpenID4VP verifier — issues the QR, polls status, checks nationality (`ALLOWED_NATIONALITIES`). QR is SVG (no Pillow dep). | 5000 |
| `eudi_login/client.py` | Streamlit | Login widget: shows the QR, polls the service, returns the verified user. | — |
| `webapp/app.py` | Streamlit | The EIS mobility dashboard — **gated by the wallet client above** (no content renders until verified). | 8501 |
| `login_app.py` | Streamlit | Standalone login demo (optional; the dashboard already gates itself). | — |

> **⚠️ PROTOTYPE verifier** — signature/trust-chain verification, key-binding, revocation, replay
> protection, and signed request objects are all mocked. Test against the sandbox **eudi-test.dev**
> (a real wallet needs an HTTPS `PUBLIC_BASE_URL`, e.g. a tunnel, to reach the callback).

## Launch

Two processes: the verifier service, then the wallet-gated site.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# Terminal 1 — verifier service (:5000).
# PUBLIC_BASE_URL must be a public HTTPS URL for a real wallet; localhost is
# fine to see the flow with the eudi-test.dev sandbox.
PUBLIC_BASE_URL=https://your-tunnel.example.com \
  .venv/bin/uvicorn eudi_login.service:app --host 0.0.0.0 --port 5000 --reload

# Terminal 2 — the gated EIS dashboard (:8501).
EUDI_API_URL=http://localhost:5000 \
ALLOWED_NATIONALITIES=PT,DE,FR,NL,IT,ES,SK \
  .venv/bin/streamlit run webapp/app.py --server.port 8501
```

Then open **http://localhost:8501** — you'll get the QR sign-in first, then the dashboard.
FastAPI auto-docs live at **http://localhost:5000/docs**.

The standalone login demo (optional): `EUDI_API_URL=http://localhost:5000 .venv/bin/streamlit run login_app.py --server.port 8502`.

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
