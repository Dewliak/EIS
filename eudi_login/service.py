# eudi_login/service.py
import base64
import json
import os
import secrets
import hashlib
import sqlite3
from datetime import datetime, timezone
from io import BytesIO
from urllib.parse import urlencode

import jwt
import qrcode
from fastapi import FastAPI, Form, Header, HTTPException
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
DATABASE_PATH = os.environ.get("DATABASE_PATH", "eis.db")

# In-memory session store (Use Redis/DB in production)
SESSIONS = {}
DEMO_SESSIONS = {}


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _db():
    parent = os.path.dirname(DATABASE_PATH)
    if parent:
        os.makedirs(parent, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def _init_database():
    connection = _db()
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS travel_registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            origin_country TEXT NOT NULL,
            destination_country TEXT NOT NULL,
            destination_region TEXT,
            travel_start TEXT NOT NULL,
            travel_end TEXT NOT NULL,
            phone_number TEXT,
            push_enabled INTEGER NOT NULL DEFAULT 1,
            status TEXT NOT NULL DEFAULT 'active',
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            fcm_token TEXT NOT NULL,
            platform TEXT NOT NULL,
            active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            UNIQUE(user_id, fcm_token)
        );
        CREATE TABLE IF NOT EXISTS hazards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            provider TEXT NOT NULL,
            provider_event_id TEXT NOT NULL,
            hazard_type TEXT NOT NULL,
            affected_region TEXT NOT NULL,
            confidence REAL NOT NULL,
            source_url TEXT,
            status TEXT NOT NULL DEFAULT 'observed',
            observed_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hazard_id INTEGER,
            issuing_country TEXT NOT NULL,
            issuer_name TEXT NOT NULL,
            severity TEXT NOT NULL,
            title TEXT NOT NULL,
            body TEXT NOT NULL,
            instructions TEXT NOT NULL,
            affected_country TEXT NOT NULL,
            affected_region TEXT NOT NULL,
            valid_from TEXT NOT NULL,
            valid_until TEXT NOT NULL,
            source_url TEXT NOT NULL,
            satellite_status TEXT NOT NULL DEFAULT 'simulated',
            status TEXT NOT NULL DEFAULT 'draft',
            created_at TEXT NOT NULL,
            published_at TEXT,
            closed_at TEXT
        );
        CREATE TABLE IF NOT EXISTS alert_recipients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alert_id INTEGER NOT NULL,
            registration_id INTEGER NOT NULL,
            delivery_status TEXT NOT NULL DEFAULT 'queued',
            acknowledged_at TEXT,
            citizen_status TEXT,
            UNIQUE(alert_id, registration_id)
        );
        CREATE TABLE IF NOT EXISTS location_consents (
            alert_id INTEGER NOT NULL,
            user_id TEXT NOT NULL,
            status TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            PRIMARY KEY(alert_id, user_id)
        );
        CREATE TABLE IF NOT EXISTS location_checkins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alert_id INTEGER NOT NULL,
            user_id TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            accuracy_meters REAL,
            captured_at TEXT NOT NULL,
            transmitted_at TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'received',
            expires_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS audit_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            actor_id TEXT NOT NULL,
            action TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """
    )
    connection.commit()
    connection.close()


_init_database()


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


class DemoSessionResponse(BaseModel):
    access_token: str
    user_id: str
    role: str


class RegistrationCreate(BaseModel):
    destination_country: str = "DE"
    destination_region: str = "Berlin"
    travel_start: str
    travel_end: str
    phone_number: str | None = None
    push_enabled: bool = True


class DeviceCreate(BaseModel):
    fcm_token: str
    platform: str = "android"


class HazardCreate(BaseModel):
    hazard_type: str = "flood"
    affected_region: str = "Berlin"
    confidence: float = 0.92
    source_url: str = "https://www.copernicus.eu/en/copernicus-services/emergency"


class AlertCreate(BaseModel):
    hazard_id: int | None = None
    issuer_name: str = "German emergency authority"
    severity: str = "high"
    title: str
    body: str
    instructions: str
    affected_country: str = "DE"
    affected_region: str = "Berlin"
    valid_from: str
    valid_until: str
    source_url: str


class LocationCheckin(BaseModel):
    latitude: float
    longitude: float
    accuracy_meters: float | None = None
    captured_at: str


def _demo_session(user_id: str, role: str) -> DemoSessionResponse:
    token = secrets.token_urlsafe(24)
    DEMO_SESSIONS[token] = {"user_id": user_id, "role": role}
    return DemoSessionResponse(access_token=token, user_id=user_id, role=role)


def _require_demo(authorization: str | None, role: str) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Bearer demo token required")
    session = DEMO_SESSIONS.get(authorization.split(" ", 1)[1])
    if not session:
        raise HTTPException(status_code=401, detail="Invalid demo token")
    if session["role"] != role:
        raise HTTPException(status_code=403, detail="Wrong demo role")
    return session["user_id"]


def _audit(connection, actor_id: str, action: str, entity_type: str, entity_id: int | str):
    connection.execute(
        "INSERT INTO audit_events(actor_id, action, entity_type, entity_id, created_at) VALUES (?, ?, ?, ?, ?)",
        (actor_id, action, entity_type, str(entity_id), _now()),
    )


def _row_dict(row):
    return dict(row) if row else None


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
# Emergency mode demo API
# ---------------------------------------------------------------------------
@app.post("/api/demo/citizen/session", response_model=DemoSessionResponse)
def create_citizen_demo_session():
    return _demo_session("demo-citizen-pt-001", "citizen")


@app.post("/api/demo/authority/session", response_model=DemoSessionResponse)
def create_authority_demo_session():
    return _demo_session("demo-authority-de-001", "authority")


@app.post("/api/citizen/registrations")
def create_registration(payload: RegistrationCreate, authorization: str | None = Header(default=None)):
    user_id = _require_demo(authorization, "citizen")
    connection = _db()
    cursor = connection.execute(
        """INSERT INTO travel_registrations
        (user_id, origin_country, destination_country, destination_region, travel_start,
         travel_end, phone_number, push_enabled, created_at)
        VALUES (?, 'PT', ?, ?, ?, ?, ?, ?, ?)""",
        (user_id, payload.destination_country.upper(), payload.destination_region,
         payload.travel_start, payload.travel_end, payload.phone_number,
         int(payload.push_enabled), _now()),
    )
    _audit(connection, user_id, "create", "travel_registration", cursor.lastrowid)
    connection.commit()
    connection.close()
    return {"id": cursor.lastrowid, "status": "active"}


@app.post("/api/devices")
def register_device(payload: DeviceCreate, authorization: str | None = Header(default=None)):
    user_id = _require_demo(authorization, "citizen")
    connection = _db()
    connection.execute(
        """INSERT INTO devices(user_id, fcm_token, platform, created_at)
        VALUES (?, ?, ?, ?) ON CONFLICT(user_id, fcm_token)
        DO UPDATE SET active=1, platform=excluded.platform""",
        (user_id, payload.fcm_token, payload.platform, _now()),
    )
    connection.commit()
    connection.close()
    return {"status": "registered", "delivery_mode": "simulated_until_firebase_configured"}


def _citizen_alert(connection, user_id: str, alert_id: int):
    row = connection.execute(
        """SELECT a.*, ar.id AS recipient_id, ar.delivery_status, ar.citizen_status,
           ar.acknowledged_at FROM alerts a
           JOIN alert_recipients ar ON ar.alert_id=a.id
           JOIN travel_registrations tr ON tr.id=ar.registration_id
           WHERE a.id=? AND tr.user_id=?""", (alert_id, user_id)
    ).fetchone()
    return _row_dict(row)


@app.get("/api/citizen/alerts")
def list_citizen_alerts(authorization: str | None = Header(default=None)):
    user_id = _require_demo(authorization, "citizen")
    connection = _db()
    rows = connection.execute(
        """SELECT DISTINCT a.*, ar.delivery_status, ar.citizen_status, ar.acknowledged_at
           FROM alerts a JOIN alert_recipients ar ON ar.alert_id=a.id
           JOIN travel_registrations tr ON tr.id=ar.registration_id
           WHERE tr.user_id=? ORDER BY a.created_at DESC""", (user_id,)
    ).fetchall()
    connection.close()
    return {"alerts": [_row_dict(row) for row in rows]}


@app.post("/api/citizen/alerts/{alert_id}/{action}")
def update_citizen_alert(alert_id: int, action: str, authorization: str | None = Header(default=None)):
    user_id = _require_demo(authorization, "citizen")
    if action not in {"acknowledge", "safe", "help"}:
        raise HTTPException(status_code=404, detail="Unknown alert action")
    connection = _db()
    row = _citizen_alert(connection, user_id, alert_id)
    if not row:
        connection.close()
        raise HTTPException(status_code=404, detail="Alert not assigned to this citizen")
    connection.execute(
        "UPDATE alert_recipients SET citizen_status=?, acknowledged_at=COALESCE(acknowledged_at, ?) WHERE id=?",
        (action, _now(), row["recipient_id"]),
    )
    _audit(connection, user_id, action, "alert", alert_id)
    connection.commit()
    connection.close()
    return {"alert_id": alert_id, "citizen_status": action}


@app.post("/api/citizen/alerts/{alert_id}/location-consent")
def grant_location_consent(alert_id: int, authorization: str | None = Header(default=None)):
    user_id = _require_demo(authorization, "citizen")
    connection = _db()
    row = _citizen_alert(connection, user_id, alert_id)
    if not row or row["status"] not in {"published", "active"}:
        connection.close()
        raise HTTPException(status_code=404, detail="Active alert not assigned to this citizen")
    connection.execute(
        """INSERT INTO location_consents(alert_id,user_id,status,expires_at) VALUES(?,?,?,?)
         ON CONFLICT(alert_id,user_id) DO UPDATE SET status='granted', expires_at=excluded.expires_at""",
        (alert_id, user_id, "granted", row["valid_until"]),
    )
    _audit(connection, user_id, "grant", "location_consent", alert_id)
    connection.commit()
    connection.close()
    return {"alert_id": alert_id, "status": "granted", "expires_at": row["valid_until"], "cadence": "once_per_day"}


@app.delete("/api/citizen/alerts/{alert_id}/location-consent")
def revoke_location_consent(alert_id: int, authorization: str | None = Header(default=None)):
    user_id = _require_demo(authorization, "citizen")
    connection = _db()
    connection.execute("UPDATE location_consents SET status='revoked' WHERE alert_id=? AND user_id=?", (alert_id, user_id))
    _audit(connection, user_id, "revoke", "location_consent", alert_id)
    connection.commit()
    connection.close()
    return {"alert_id": alert_id, "status": "revoked"}


@app.post("/api/citizen/alerts/{alert_id}/location-checkins")
def create_location_checkin(alert_id: int, payload: LocationCheckin, authorization: str | None = Header(default=None)):
    user_id = _require_demo(authorization, "citizen")
    connection = _db()
    consent = connection.execute(
        "SELECT * FROM location_consents WHERE alert_id=? AND user_id=? AND status='granted'", (alert_id, user_id)
    ).fetchone()
    if not consent:
        connection.close()
        raise HTTPException(status_code=403, detail="Explicit location consent required")
    latest = connection.execute(
        "SELECT transmitted_at FROM location_checkins WHERE alert_id=? AND user_id=? ORDER BY id DESC LIMIT 1", (alert_id, user_id)
    ).fetchone()
    if latest:
        previous = datetime.fromisoformat(latest["transmitted_at"])
        if (datetime.now(timezone.utc) - previous).total_seconds() < 86400:
            connection.close()
            raise HTTPException(status_code=429, detail="Daily check-in already received")
    connection.execute(
        """INSERT INTO location_checkins(alert_id,user_id,latitude,longitude,accuracy_meters,captured_at,transmitted_at,expires_at)
           VALUES(?,?,?,?,?,?,?,?)""",
        (alert_id, user_id, payload.latitude, payload.longitude, payload.accuracy_meters,
         payload.captured_at, _now(), consent["expires_at"]),
    )
    _audit(connection, user_id, "submit", "location_checkin", alert_id)
    connection.commit()
    connection.close()
    return {"alert_id": alert_id, "status": "received", "next_checkin": "after_24_hours"}


@app.post("/api/authority/hazards/simulate")
def simulate_hazard(payload: HazardCreate, authorization: str | None = Header(default=None)):
    authority_id = _require_demo(authorization, "authority")
    connection = _db()
    event_id = f"SIM-{secrets.token_hex(6).upper()}"
    cursor = connection.execute(
        """INSERT INTO hazards(provider,provider_event_id,hazard_type,affected_region,confidence,source_url,observed_at)
           VALUES(?,?,?,?,?,?,?)""",
        ("simulated-copernicus", event_id, payload.hazard_type, payload.affected_region,
         payload.confidence, payload.source_url, _now()),
    )
    _audit(connection, authority_id, "simulate", "hazard", cursor.lastrowid)
    connection.commit()
    row = connection.execute("SELECT * FROM hazards WHERE id=?", (cursor.lastrowid,)).fetchone()
    connection.close()
    return _row_dict(row)


@app.get("/api/authority/hazards")
def list_hazards(authorization: str | None = Header(default=None)):
    _require_demo(authorization, "authority")
    connection = _db()
    rows = connection.execute("SELECT * FROM hazards ORDER BY observed_at DESC").fetchall()
    connection.close()
    return {"hazards": [_row_dict(row) for row in rows]}


@app.post("/api/authority/hazards/{hazard_id}/review")
def review_hazard(hazard_id: int, authorization: str | None = Header(default=None)):
    authority_id = _require_demo(authorization, "authority")
    connection = _db()
    cursor = connection.execute("UPDATE hazards SET status='reviewed' WHERE id=?", (hazard_id,))
    if not cursor.rowcount:
        connection.close()
        raise HTTPException(status_code=404, detail="Hazard not found")
    _audit(connection, authority_id, "review", "hazard", hazard_id)
    connection.commit()
    connection.close()
    return {"hazard_id": hazard_id, "status": "reviewed"}


@app.post("/api/authority/alerts")
def create_alert(payload: AlertCreate, authorization: str | None = Header(default=None)):
    authority_id = _require_demo(authorization, "authority")
    connection = _db()
    cursor = connection.execute(
        """INSERT INTO alerts(hazard_id,issuing_country,issuer_name,severity,title,body,instructions,
           affected_country,affected_region,valid_from,valid_until,source_url,created_at)
           VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (payload.hazard_id, "DE", payload.issuer_name, payload.severity, payload.title, payload.body,
         payload.instructions, payload.affected_country.upper(), payload.affected_region,
         payload.valid_from, payload.valid_until, payload.source_url, _now()),
    )
    _audit(connection, authority_id, "create", "alert", cursor.lastrowid)
    connection.commit()
    row = connection.execute("SELECT * FROM alerts WHERE id=?", (cursor.lastrowid,)).fetchone()
    connection.close()
    return _row_dict(row)


@app.get("/api/authority/alerts")
def list_authority_alerts(authorization: str | None = Header(default=None)):
    _require_demo(authorization, "authority")
    connection = _db()
    rows = connection.execute(
        """SELECT a.*, COUNT(ar.id) AS recipient_count FROM alerts a
           LEFT JOIN alert_recipients ar ON ar.alert_id=a.id GROUP BY a.id ORDER BY a.created_at DESC"""
    ).fetchall()
    connection.close()
    return {"alerts": [_row_dict(row) for row in rows]}


@app.post("/api/authority/alerts/{alert_id}/publish")
def publish_alert(alert_id: int, authorization: str | None = Header(default=None)):
    authority_id = _require_demo(authorization, "authority")
    connection = _db()
    alert = connection.execute("SELECT * FROM alerts WHERE id=?", (alert_id,)).fetchone()
    if not alert:
        connection.close()
        raise HTTPException(status_code=404, detail="Alert not found")
    if alert["status"] not in {"draft", "reviewed"}:
        connection.close()
        raise HTTPException(status_code=409, detail="Alert is not publishable")
    registrations = connection.execute(
        """SELECT id FROM travel_registrations WHERE status='active' AND destination_country=?
           AND destination_region=? AND travel_start <= ? AND travel_end >= ?""",
        (alert["affected_country"], alert["affected_region"], alert["valid_until"], alert["valid_from"]),
    ).fetchall()
    for registration in registrations:
        connection.execute(
            "INSERT OR IGNORE INTO alert_recipients(alert_id,registration_id,delivery_status) VALUES(?,?,?)",
            (alert_id, registration["id"], "simulated_sent"),
        )
    connection.execute("UPDATE alerts SET status='published', published_at=? WHERE id=?", (_now(), alert_id))
    _audit(connection, authority_id, "publish", "alert", alert_id)
    connection.commit()
    connection.close()
    return {"alert_id": alert_id, "status": "published", "recipient_count": len(registrations), "delivery_mode": "simulated"}


@app.post("/api/authority/alerts/{alert_id}/close")
def close_alert(alert_id: int, authorization: str | None = Header(default=None)):
    authority_id = _require_demo(authorization, "authority")
    connection = _db()
    cursor = connection.execute("UPDATE alerts SET status='closed', closed_at=? WHERE id=?", (_now(), alert_id))
    if not cursor.rowcount:
        connection.close()
        raise HTTPException(status_code=404, detail="Alert not found")
    _audit(connection, authority_id, "close", "alert", alert_id)
    connection.commit()
    connection.close()
    return {"alert_id": alert_id, "status": "closed"}


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
