"""
EIS — European Impact Sprints
Streamlit front-end for the unified mobility platform.

This is the **Portugal-hosted instance**: origin is fixed to Portugal, the user
picks a destination, an intent (traveling / moving), and a subject, then lands
in the Deadlines · Documents · Information dashboard described in
docs/00-PLATFORM-CONCEPT.md and docs/09-FULL-PLATFORM-SPEC.md.

Real, sourced content exists for Germany (the focus) and Spain. The other seven
destinations show rough/unverified matrix data, badged as such.

Run:  streamlit run webapp/app.py
"""

import os
import sys
from pathlib import Path

import streamlit as st

# ``streamlit run webapp/app.py`` puts webapp/ on sys.path.  Add the project
# root so the sibling EUDI login package is available in that normal run mode.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import data
from eudi_login.client import EUDIWalletLogin

st.set_page_config(page_title="EIS — European Impact Sprints", page_icon="🇪🇺", layout="wide")


# ---------------------------------------------------------------------------
# Navigation state
# ---------------------------------------------------------------------------

def _init_state():
    st.session_state.setdefault("country", None)
    st.session_state.setdefault("intent", None)
    st.session_state.setdefault("subject", None)


def _wallet_login() -> EUDIWalletLogin:
    """Create the EUDI client from deployment configuration."""
    allowed_nationalities = {
        nationality.strip().upper()
        for nationality in os.environ.get("ALLOWED_NATIONALITIES", "PT,DE,FR,NL,IT,ES,SK").split(",")
        if nationality.strip()
    }
    return EUDIWalletLogin(
        api_base_url=os.environ.get("EUDI_API_URL", "http://localhost:5000"),
        allowed_nationalities=allowed_nationalities,
    )


def _reset(to_step):
    """Clear state from a given step onward."""
    order = ["country", "intent", "subject"]
    for key in order[order.index(to_step):]:
        st.session_state[key] = None


_init_state()


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

def header(user):
    left, right = st.columns([0.75, 0.25])
    with left:
        st.markdown("## 🇪🇺 EIS — European Impact Sprints")
        st.caption(
            f"Portugal-hosted instance · Origin fixed to **{data.ORIGIN['flag']} "
            f"{data.ORIGIN['name']}** · One interface for documents, deadlines and information "
            f"across Europe."
        )
    with right:
        st.markdown(" ")
        st.caption(f"Wallet verified · {', '.join(user.nationalities)}")
        if st.button("Sign out", use_container_width=True):
            _wallet_login().sign_out()
            _reset("country")
            st.rerun()
        if st.button("↺ Start over", use_container_width=True):
            _reset("country")
            st.rerun()


def breadcrumb():
    parts = [f"{data.ORIGIN['flag']} Portugal"]
    if st.session_state.country:
        c = data.get_country(st.session_state.country)
        parts.append(f"{c['flag']} {c['name']}")
    if st.session_state.intent:
        i = next(x for x in data.INTENTS if x["id"] == st.session_state.intent)
        parts.append(f"{i['icon']} {i['name']}")
    if st.session_state.subject:
        s = next(x for x in data.SUBJECTS if x["id"] == st.session_state.subject)
        parts.append(f"{s['icon']} {s['name']}")
    st.markdown(" → ".join(parts))
    st.divider()


# ---------------------------------------------------------------------------
# Step 1 — destination picker
# ---------------------------------------------------------------------------

def step_country():
    st.subheader("Where are you going?")
    st.write("Pick your destination country. Germany and Spain carry verified content; other "
             "destinations show rough draft data for now.")

    cols = st.columns(5)
    for idx, c in enumerate(data.COUNTRIES):
        with cols[idx % 5]:
            label = f"{c['flag']} {c['name']}"
            if not c["verified"]:
                label += "  ·  draft"
            if st.button(label, key=f"country_{c['code']}", use_container_width=True):
                st.session_state.country = c["code"]
                _reset("intent")
                st.rerun()

    st.caption("🇩🇪 Germany is the primary worked case (Portugal → Germany). "
               "Countries marked *draft* use unverified matrix data (docs/11).")


# ---------------------------------------------------------------------------
# Step 2 — intent
# ---------------------------------------------------------------------------

def step_intent():
    c = data.get_country(st.session_state.country)
    st.subheader(f"Traveling to {c['flag']} {c['name']}, or moving in?")
    cols = st.columns(2)
    for idx, i in enumerate(data.INTENTS):
        with cols[idx]:
            with st.container(border=True):
                st.markdown(f"### {i['icon']} {i['name']}")
                st.write(i["sub"])
                if st.button(f"Choose {i['name']}", key=f"intent_{i['id']}", use_container_width=True):
                    st.session_state.intent = i["id"]
                    _reset("subject")
                    st.rerun()


# ---------------------------------------------------------------------------
# Step 3 — subject
# ---------------------------------------------------------------------------

def step_subject():
    st.subheader("What do you need help with?")
    st.caption("Only **Residence & Registration** is live in this MVP. Other subjects are planned.")
    cols = st.columns(4)
    for idx, s in enumerate(data.SUBJECTS):
        with cols[idx % 4]:
            label = f"{s['icon']} {s['name']}"
            if st.button(label, key=f"subject_{s['id']}", use_container_width=True, disabled=not s["live"]):
                st.session_state.subject = s["id"]
                st.rerun()
            if not s["live"]:
                st.caption("coming soon")


# ---------------------------------------------------------------------------
# Step 4 — dashboard
# ---------------------------------------------------------------------------

def inform_with_id():
    """The wallet-gated travel-notification button (stub for now)."""
    with st.container(border=True):
        cols = st.columns([0.7, 0.3])
        with cols[0]:
            st.markdown("**🪪 Inform with ID** — notify your destination (and Portugal) that you are "
                        "traveling, using the EU Digital Identity Wallet.")
            st.caption("Wallet-gated feature. EUDI Wallets become mandatory 24 Dec 2026; production "
                       "wallets land ~2027 (docs/09 §6.2). Disabled until the wallet layer is wired in.")
        with cols[1]:
            st.button("Inform with ID", disabled=True, use_container_width=True,
                      help="Coming with the EUDI Wallet integration (~2027).")


def dashboard():
    c = data.get_country(st.session_state.country)
    intent = st.session_state.intent
    content = data.get_content(c["code"], intent, st.session_state.subject)

    if content is None:
        st.warning("No content available for this combination yet.")
        return

    if not content["verified"]:
        st.warning("⚠️ **Rough / unverified data.** This destination's long-stay content comes from "
                   "the draft 8-country matrix and has not been verified against primary sources. "
                   "Germany and Spain are the verified cases.")
    else:
        st.success("✅ Verified content — sourced from primary references (see the Information tab).")

    st.info(content["summary"])
    inform_with_id()

    tab_dl, tab_docs, tab_info = st.tabs(["📅 Deadlines", "📄 Documents", "ℹ️ Information"])

    with tab_dl:
        st.markdown("#### The compliance clock")
        st.dataframe(
            [{"Trigger": d["trigger"], "Action": d["action"], "Deadline": d["window"], "Fine": d["fine"]}
             for d in content["deadlines"]],
            use_container_width=True, hide_index=True,
        )

    with tab_docs:
        st.markdown("#### Documents & forms")
        for doc in content["documents"]:
            with st.expander(f"📄 {doc['name']}"):
                st.write(doc["initial_info"])
                meta = {
                    "Information shared": doc["shared"],
                    "To whom": doc["to_whom"],
                    "How long kept": doc["retention"],
                    "Reissuable?": doc["reissuable"],
                    "Where submitted": doc["submit_where"],
                    "Issuer": doc["issuer"],
                }
                for k, v in meta.items():
                    st.markdown(f"- **{k}:** {v}")
                bcols = st.columns(2)
                with bcols[0]:
                    if doc["form_url"]:
                        st.markdown(f"[📎 Open form / source]({doc['form_url']})")
                with bcols[1]:
                    st.button("🖊️ Sign with wallet", key=f"sign_{doc['name']}", disabled=True,
                              help="Document signing arrives with the EUDI Wallet integration (~2027).",
                              use_container_width=True)

    with tab_info:
        st.markdown("#### Rules, thresholds & contacts")
        st.dataframe(
            [{"Rule": r[0], "Value": r[1], "Source": r[2]} for r in content["info"]],
            use_container_width=True, hide_index=True,
        )
        st.markdown("#### Sources")
        for s in content["sources"]:
            st.markdown(f"- {s}")


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

def main():
    user = _wallet_login().authenticate()
    if user is None or not user.verified:
        st.stop()

    header(user)
    breadcrumb()

    if st.session_state.country is None:
        step_country()
    elif st.session_state.intent is None:
        step_intent()
    elif st.session_state.subject is None:
        step_subject()
    else:
        dashboard()

    st.divider()
    st.caption("EIS prototype · access is protected by the EUDI Wallet verifier service · "
               "content per docs/ · not legal advice.")


if __name__ == "__main__":
    main()
