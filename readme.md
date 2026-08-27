# EIS — European Impact Sprints

Unified European mobility platform + EU Digital Identity Wallet identity/emergency layer.

> **Origin → Destination worked example:** Portuguese citizens → Germany (Berlin).
> Third-country validation: Spain (see `documentation/10-SPAIN-VALIDATION.md`).

## The project

Two parts, one repo:

| Part | Where | What |
|---|---|---|
| **Code** | `app.py`, `requirements.txt` | EUDI Wallet OpenID4VP verifier prototype (Flask) |
| **Research & spec** | `documentation/00`–`documentation/11` | Personas, case walkthroughs, documents index, full platform spec, sources, PDF forms |

## Code — `app.py` (prototype)

A minimal OpenID4VP **Relying Party (verifier)** that logs a user in with their EU Digital
Identity Wallet, gated by nationality:

| Route | Purpose |
|---|---|
| `/login` | Builds a DCQL query asking the wallet for the PID `nationality` claim, shows it as QR |
| `/qr` | Renders the QR code |
| `/callback` | Receives the wallet's `vp_token`, extracts `nationality`, allow-lists it |
| `/status/<id>` | Polled by the browser for completion |
| `/result/<id>` | Shows verified / rejected / error |

**⚠️ PROTOTYPE, NOT PRODUCTION.** Signature + trust-chain verification, key-binding, revocation,
replay protection, and signed request objects (JAR) are all **mocked** (see comments in the file).

### Run

```bash
pip install -r requirements.txt

# HTTPS needed — the wallet must reach /callback over https.
# Local dev: use a tunnel
cloudflared tunnel --url http://localhost:5000   # or: ngrok http 5000
PUBLIC_BASE_URL=https://your-tunnel.example.com python app.py
```

Test against the public sandbox **eudi-test.dev** (needs https to reach your `/callback`).

### Config

- `ALLOWED_NATIONALITIES` — ISO 3166-1 alpha-2 codes allowed to log in (default `DE, FR, NL, IT, ES`).
- `PID_VCT` — `eu.europa.ec.eudi.pid.1` (ARF PID credential type).
- `PUBLIC_BASE_URL` — where the wallet POSTs back.

## Research & spec — `documentation/`

| # | Doc | Content |
|---|---|---|
| 00 | Platform concept | Vision, user flow, tabs, EUDI + emergency |
| 01 | Personas | Tiago (travel) + Beatriz (move) — Portuguese → Germany |
| 02 | Traveling case | PT→DE <3 months: ID only, no registration |
| 03 | Moving case | PT→DE: Anmeldung 14-day rule, no CRUE |
| 04 | Documents index | Master tables + DE/PT/ES contrast |
| 05 | Sources | Verified primary + secondary |
| 06 | PDF URLs | Forms + fetched assets |
| 07 | Assisting platforms | Existing EU/DE/PT platforms |
| 08 | EUDI Wallet | eIDAS 2.0 timeline + use cases |
| 09 | **Full platform spec** | **Master spec: web + mobile + EUDI + emergency, data model, research plan** |
| 10 | Spain validation | 3rd country confirms the three-clock pattern |
| 11 | Country matrix | 27-country fact matrix |
| 12 | **Subcategories** | **The 7 cases (T1 + M1–M6) that need different procedures** |
| — | `cases/` | **Per-case docs: info, procedures, deadlines, documents, URLs** |
| — | `assets/pdf/` | Fetched forms (DE landlord confirmation, DE §5 notice, PT CRUE) |

**Start at `documentation/09-FULL-PLATFORM-SPEC.md`** (master spec) and
**`documentation/12-SUBCATEGORIES.md`** (the case taxonomy).

## Status

Research + specification phase. `app.py` is the only code, and it's a prototype verifier.
Next per `documentation/09` §10: build the 27-country fact matrix, track wallet rollout, spec the MVP.
> curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
> chmod +x cloudflared && sudo mv cloudflared /usr/local/bin/
after that: 
> cloudflared tunnel --url http://localhost:5000
> 
 using python 3.13 \

> sudo dnf install python3.13 python3.13-devel python3.13-venv -y \

C libs for PIllow

> sudo dnf install libjpeg-turbo-devel zlib-devel libtiff-devel freetype-devel lcms2-devel libwebp-devel tcl-devel tk-devel -y

> 1. start fastapi: uvicorn eudi_login.service:app --host 0.0.0.0 --port 5000 --reload
> 2. start streamlit login page: streamlit run app.py --server.port 8501
