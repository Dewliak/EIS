# eudi_login/service.py
import base64
import json
import os
import secrets
import hashlib
from io import BytesIO
from urllib.parse import urlencode

import jwt
import qrcode
from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="EUDI Login Service")

# Allow Streamlit (typically port 8501) to call this service
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
PUBLIC_BASE_URL = os.environ.get("PUBLIC_BASE_URL", "https://your-tunnel.example.com")
ALLOWED_NATIONALITIES = set(os.environ.get("ALLOWED_NATIONALITIES", "DE,FR,NL,IT,ES,SK").split(","))
PID_VCT_CANDIDATES = ["urn:eudi:pid:de:1", "urn:eudi:pid:1", "eu.europa.ec.eudi.pid.1"]

# In-memory session store (Use Redis/DB in production)
SESSIONS = {}


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class LoginResponse(BaseModel):
    state: str
    qr_code_base64: str
    sandbox_link: str


class StatusResponse(BaseModel):
    status: str  # "pending", "verified", "rejected", "error"
    nationalities: list[str] | None = None
    error: str | None = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/health")
def health():
    """Lightweight health check for Docker and Railway."""
    return {"status": "ok"}


@app.post("/login", response_model=LoginResponse)
def initiate_login():
    state = secrets.token_urlsafe(16)
    nonce = secrets.token_urlsafe(16)

    dcql_query = {
        "credentials": [
            {
                "id": "eu_pid",
                "format": "dc+sd-jwt",
                "meta": {"vct_values": PID_VCT_CANDIDATES},
                "claims": [{"path": ["nationalities"]}],
            }
        ]
    }

    auth_request_params = {
        "response_type": "vp_token",
        "client_id": PUBLIC_BASE_URL,
        "response_uri": f"{PUBLIC_BASE_URL}/callback",
        "response_mode": "direct_post",
        "nonce": nonce,
        "state": state,
        "dcql_query": json.dumps(dcql_query),
    }

    deep_link = "openid4vp://?" + urlencode(auth_request_params)
    sandbox_link = deep_link.replace("openid4vp://", "https://eudi-test.dev/authorize")

    # Generate QR code as base64 string for easy Streamlit rendering
    img = qrcode.make(deep_link)
    buf = BytesIO()
    img.save(buf, format="PNG")
    qr_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    SESSIONS[state] = {"status": "pending", "nonce": nonce, "deep_link": deep_link}

    return LoginResponse(state=state, qr_code_base64=qr_base64, sandbox_link=sandbox_link)


@app.post("/callback")
def receive_callback(state: str = Form(...), vp_token: str = Form(...)):
    session = SESSIONS.get(state)
    if not session:
        raise HTTPException(status_code=400, detail="unknown or expired session")

    if not vp_token:
        SESSIONS[state]["status"] = "error"
        SESSIONS[state]["error"] = "no vp_token in response"
        return {"ok": True}

    try:
        vp_token_json = json.loads(vp_token)
        credentials = vp_token_json.get("eu_pid")
        if not credentials or not isinstance(credentials, list):
            raise ValueError("eu_pid missing or invalid in vp_token")

        nationalities = extract_nationalities(credentials[0])
        allowed = any(n in ALLOWED_NATIONALITIES for n in nationalities)

        SESSIONS[state].update(
            status="verified" if allowed else "rejected",
            nationalities=nationalities,
        )
    except Exception as exc:
        SESSIONS[state].update(status="error", error=str(exc))

    return {"ok": True}


@app.get("/status/{state}", response_model=StatusResponse)
def get_status(state: str):
    session = SESSIONS.get(state)
    if not session:
        raise HTTPException(status_code=404, detail="Unknown session")

    return StatusResponse(
        status=session.get("status"),
        nationalities=session.get("nationalities"),
        error=session.get("error")
    )


# ---------------------------------------------------------------------------
# Mocked SD-JWT Parser (KEEP PROTOTYPE WARNINGS)
# ---------------------------------------------------------------------------
def _b64url_decode(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def _b64url_digest(disclosure_str: str) -> str:
    return base64.urlsafe_b64encode(
        hashlib.sha256(disclosure_str.encode()).digest()
    ).rstrip(b"=").decode()


def extract_nationalities(vp_token: str) -> list[str]:
    """
    MOCKED / NOT SAFE FOR PRODUCTION:
    - Decodes JWT without verifying signature.
    - No Key Binding, nonce/aud checks, or revocation status checks.
    - Hand-rolled digest resolution; use a proper SD-JWT library in production.
    """
    parts = vp_token.split("~")
    disclosure_strs = [p for p in parts[1:] if p]

    # Unverified decode
    jwt.decode(parts[0], options={"verify_signature": False})

    by_digest = {}
    for d in disclosure_strs:
        try:
            parsed = json.loads(_b64url_decode(d))
            by_digest[_b64url_digest(d)] = parsed
        except Exception:
            continue

    for parsed in by_digest.values():
        if len(parsed) == 3 and parsed[1] == "nationalities":
            raw_array = parsed[2]
            resolved = []
            for item in raw_array:
                if isinstance(item, dict) and "..." in item:
                    ref = by_digest.get(item["..."])
                    if ref and len(ref) == 2:
                        resolved.append(ref[1])
                else:
                    resolved.append(item)
            return resolved
    return []
