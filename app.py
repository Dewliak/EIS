"""
EUDI Wallet "login with your country" demo
===========================================

A minimal OpenID4VP Relying Party (verifier) in Flask:

  1. /login        - starts a session, builds an OpenID4VP authorization
                      request asking the wallet for the PID credential's
                      `nationality` claim, and shows it as a QR code.
  2. /callback      - the wallet POSTs its response (vp_token) here.
  3. /status/<id>   - polled by the browser to know when the wallet has
                      responded.
  4. /result/<id>   - shows whether the user is allowed in.

THIS IS A PROTOTYPE, NOT A PRODUCTION VERIFIER.
See the "MOCKED / NOT SAFE FOR PRODUCTION" comments below for exactly
what's cut and what you'd need to add for real use (trust-chain and
signature verification, key-binding checks, revocation/status-list
checks, replay protection, signed request objects).

Test it against the public EUDI Dev Wallet sandbox: https://eudi-test.dev
(that sandbox needs to reach your /callback over https, so run this
behind a tunnel like `ngrok http 5000` during local testing and set
PUBLIC_BASE_URL accordingly).
"""

import base64
import json
import os
import secrets
from io import BytesIO
from urllib.parse import urlencode

import jwt  # pip install pyjwt
import qrcode
from flask import Flask, jsonify, request, send_file, render_template_string

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

# Where your app is publicly reachable (the wallet must be able to POST here).
# During local dev, point this at your ngrok/tunnel URL.
PUBLIC_BASE_URL = os.environ.get("PUBLIC_BASE_URL", "https://your-tunnel.example.com")

# ISO 3166-1 alpha-2 country codes allowed to log in.
ALLOWED_NATIONALITIES = {"DE", "FR", "NL", "IT", "ES"}

# The PID credential type as defined in the ARF's PID Rulebook.
PID_VCT = "eu.europa.ec.eudi.pid.1"

# In-memory session store — fine for a prototype, use a real store (Redis, DB)
# for anything more than a demo.
SESSIONS = {}


# ---------------------------------------------------------------------------
# 1. Start login: build the OpenID4VP authorization request
# ---------------------------------------------------------------------------

@app.route("/login")
def login():
    state = secrets.token_urlsafe(16)
    nonce = secrets.token_urlsafe(16)
    SESSIONS[state] = {"status": "pending", "nonce": nonce}

    # DCQL (Digital Credentials Query Language) query: ask for the PID
    # credential and only the `nationality` claim from it — selective
    # disclosure means the wallet won't hand over anything else.
    dcql_query = {
        "credentials": [
            {
                "id": "eu_pid",
                "format": "dc+sd-jwt",
                "meta": {"vct_values": [PID_VCT]},
                "claims": [{"path": ["nationality"]}],
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

    # NOTE (mocked): real Relying Parties must sign this as a JWT
    # ("Request Object" / JAR) with a certificate chaining to a trusted
    # EU/member-state trust list, so the wallet can verify who's asking
    # before showing the consent screen. Sending it unsigned here is fine
    # for a sandbox wallet but wouldn't be accepted by a real production
    # wallet or pass certification.
    deep_link = "openid4vp://?" + urlencode(auth_request_params)

    return render_template_string(
        """
        <h2>Sign in with your EU Digital Identity Wallet</h2>
        <p>Scan this with the EUDI Wallet app, or open the sandbox wallet
           directly if you're testing on the same device.</p>
        <img src="/qr?state={{ state }}" width="260">
        <p><a href="{{ link }}">Open in wallet</a></p>
        <p><a href="https://eudi-test.dev/?request={{ link|urlencode }}"
              target="_blank">Open in EUDI Dev Wallet sandbox</a></p>
        <script>
          const poll = setInterval(async () => {
            const r = await fetch('/status/{{ state }}');
            const d = await r.json();
            if (d.status !== 'pending') {
              clearInterval(poll);
              window.location = '/result/{{ state }}';
            }
          }, 2000);
        </script>
        """,
        state=state,
        link=deep_link,
    )


@app.route("/qr")
def qr():
    state = request.args.get("state")
    session = SESSIONS.get(state)
    if not session:
        return "unknown session", 404
    # Rebuild the same deep link to encode as a QR code.
    img = qrcode.make(f"{PUBLIC_BASE_URL}/login?state={state}")
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")


# ---------------------------------------------------------------------------
# 2. Wallet response
# ---------------------------------------------------------------------------

@app.route("/callback", methods=["POST"])
def callback():
    state = request.form.get("state")
    vp_token = request.form.get("vp_token")

    session = SESSIONS.get(state)
    if not session:
        return jsonify({"error": "unknown or expired session"}), 400
    if not vp_token:
        session.update(status="error", error="no vp_token in response")
        return jsonify({"error": "missing vp_token"}), 400

    try:
        nationality = extract_nationality(vp_token)
    except Exception as exc:  # noqa: BLE001 - demo-level error handling
        session.update(status="error", error=str(exc))
        return jsonify({"error": "could not parse presentation"}), 400

    if nationality in ALLOWED_NATIONALITIES:
        session.update(status="verified", nationality=nationality)
    else:
        session.update(status="rejected", nationality=nationality)

    return jsonify({"ok": True})


def extract_nationality(vp_token: str) -> str | None:
    """
    Parse an SD-JWT VC presentation and pull out the disclosed
    `nationality` claim.

    MOCKED / NOT SAFE FOR PRODUCTION:
      - We decode the JWT without verifying its signature. A real verifier
        must check the signature against the issuer's key, and check that
        the issuer's certificate chains to a trusted list (member-state PID
        provider trust anchors, per the ARF).
      - We don't verify Key Binding (proof the presenter actually holds the
        credential), don't check `nonce`/`aud` on the KB-JWT, and don't
        check the credential's status list for revocation.
      - Real SD-JWT VC parsing should use a proper library (e.g. an SD-JWT
        implementation) rather than hand-rolled base64 splitting — this is
        simplified for readability.
    """
    parts = vp_token.split("~")
    credential_jwt = parts[0]
    disclosures = parts[1:]

    # Unverified decode — see docstring warning above.
    jwt.decode(credential_jwt, options={"verify_signature": False})

    for disclosure in disclosures:
        if not disclosure:
            continue
        try:
            padded = disclosure + "=" * (-len(disclosure) % 4)
            salt, claim_name, claim_value = json.loads(
                base64.urlsafe_b64decode(padded)
            )
        except Exception:
            continue  # not a claim disclosure (e.g. trailing KB-JWT)
        if claim_name == "nationality":
            return claim_value

    return None


# ---------------------------------------------------------------------------
# 3 & 4. Status polling + result page
# ---------------------------------------------------------------------------

@app.route("/status/<state>")
def status(state):
    session = SESSIONS.get(state, {"status": "unknown"})
    return jsonify({"status": session.get("status")})


@app.route("/result/<state>")
def result(state):
    session = SESSIONS.get(state)
    if not session:
        return "Unknown session.", 404
    if session["status"] == "verified":
        return f"✅ Welcome! Verified nationality: {session['nationality']}"
    if session["status"] == "rejected":
        return f"⛔ Access denied. Nationality '{session['nationality']}' isn't on the allow-list."
    if session["status"] == "error":
        return f"⚠️ Verification failed: {session.get('error')}"
    return "Still waiting for the wallet..."


if __name__ == "__main__":
    app.run(debug=True, port=5000)