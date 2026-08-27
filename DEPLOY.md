# Deploy — Railway

Two Railway services from this one repo. **No tunnel** — Railway gives each service a
public HTTPS domain, which is exactly what a local `cloudflared`/`ngrok` tunnel stands in for.

```
Service A  "eudi-verifier"   FastAPI    → https://eudi-verifier-xxxx.up.railway.app
Service B  "eis-web"         Streamlit  → https://eis-web-xxxx.up.railway.app
                             (calls A server-side via requests)
```

Railway injects `$PORT` into each service — bind to it, never a hard-coded port.

## Service A — eudi-verifier

| Setting | Value |
|---|---|
| Start command | `uvicorn eudi_login.service:app --host 0.0.0.0 --port $PORT` |
| `PUBLIC_BASE_URL` | this service's **own** public domain (the wallet callback returns here) |
| `ALLOWED_NATIONALITIES` | `PT,DE,FR,NL,IT,ES,SK` |

Set `PUBLIC_BASE_URL` **after** the first deploy assigns the domain, then redeploy.

## Service B — eis-web

| Setting | Value |
|---|---|
| Start command | `streamlit run webapp/app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true` |
| `EUDI_API_URL` | Service A's URL — public `https://eudi-verifier-xxxx.up.railway.app`, or the private `http://<A>.railway.internal:$PORT` (client.py calls it server-side, so private works and saves egress) |
| `ALLOWED_NATIONALITIES` | same as A |

## Notes

- `requirements.txt` is auto-detected (Nixpacks). The `Procfile` documents both process
  commands; each Railway service overrides its own start command per the tables above.
- QR is SVG (no Pillow), so no system image libraries are needed in the build.
- Local Python is 3.14; if a Railway build hits a wheel gap, pin a stable runtime
  (e.g. add `.python-version` with `3.12`).
- Still a **prototype verifier** — no production-grade signature / trust-chain / key-binding /
  revocation checks. Fine for a demo; not for real identity verification.
