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

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

### Local dev

The wallet QR gate is always on. The wallet POSTs its response to the verifier's `/callback`,
so the verifier must be reachable over **public HTTPS** — locally that means a tunnel (a stand-in
for the public URL you get for free on Railway).

```bash
# Terminal 1 — tunnel (gives you a public HTTPS URL for :5000)
cloudflared tunnel --url http://localhost:5000        # or: ngrok http 5000

# Terminal 2 — verifier service. PUBLIC_BASE_URL = the tunnel URL from Terminal 1.
PUBLIC_BASE_URL=https://your-tunnel.trycloudflare.com \
  .venv/bin/uvicorn eudi_login.service:app --host 0.0.0.0 --port 5000 --reload

# Terminal 3 — the gated EIS dashboard.
EUDI_API_URL=http://localhost:5000 \
ALLOWED_NATIONALITIES=PT,DE,FR,NL,IT,ES,SK \
  .venv/bin/streamlit run webapp/app.py --server.port 8501
```

FastAPI auto-docs: **http://localhost:5000/docs**. Standalone login demo (optional):
`EUDI_API_URL=http://localhost:5000 .venv/bin/streamlit run login_app.py --server.port 8502`.

### Deploy (Railway) — no tunnel

Railway hands each service a public HTTPS domain, which **replaces the tunnel**. See
[`DEPLOY.md`](DEPLOY.md).

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
