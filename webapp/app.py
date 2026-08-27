"""
 EU Data Compass
Streamlit front-end for the unified mobility platform.

This is the **Portugal-hosted instance**: origin is fixed to Portugal, the user
picks a destination, an intent (traveling / moving), and a subject, then lands
in the Deadlines · Documents · Information dashboard described in
docs/02-spec/PLATFORM-CONCEPT.md and docs/02-spec/PLATFORM-SPEC.md
(build target: docs/01-plan/IMPLEMENTATION-PLAN.md).

Real, sourced content exists for Germany (the focus) and Spain. The other seven
destinations show rough/unverified matrix data, badged as such.

Run:  streamlit run webapp/app.py
"""

import os
import sys
from html import escape
from pathlib import Path

import streamlit as st

# ``streamlit run webapp/app.py`` puts webapp/ on sys.path.  Add the project
# root so the sibling EUDI login package is available in that normal run mode.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import data
from eudi_login.client import EUDIWalletLogin

st.set_page_config(page_title="EU Data Compass", layout="wide")

st.markdown(
    """
    <style>
      :root { --eu-blue: #164194; --ink: #172b4d; --muted: #52627a; }
      html, body, [class*="css"] { font-size: 17px; }
      .stApp { background: #f7f9fc; color: var(--ink); }
      [data-testid="stMainBlockContainer"] { max-width: 1180px; padding-top: 2.25rem; }
      h1, h2, h3 { color: var(--ink); letter-spacing: -0.02em; }
      h2 { font-size: 2rem !important; }
      h3 { font-size: 1.35rem !important; }
      p, label, .stCaption, [data-testid="stMarkdownContainer"] { line-height: 1.55; }
      .app-kicker { color: var(--eu-blue); font-size: .8rem; font-weight: 800; letter-spacing: .11em; text-transform: uppercase; }
      .app-title { color: var(--ink); font-size: clamp(2rem, 4vw, 3rem); font-weight: 800; line-height: 1.05; margin: .3rem 0 .55rem; }
      .stButton > button, .stSelectbox [data-baseweb="select"] { min-height: 2.9rem; font-size: 1rem; }
      .stButton > button { border-radius: .45rem; }
      [data-testid="stDataFrame"] { font-size: 1rem; }
      .deadline-timeline { position: relative; max-width: 900px; margin: 1.25rem 0 1rem; padding: .25rem 0; }
      .deadline-timeline::before { content: ""; position: absolute; left: 1.05rem; top: 1.6rem; bottom: 1.6rem; width: 2px; background: #c8d7ec; }
      .deadline-item { position: relative; display: grid; grid-template-columns: 2.15rem 1fr; gap: 1.1rem; padding: .7rem 0 1.05rem; }
      .deadline-marker { position: relative; z-index: 1; display: flex; align-items: center; justify-content: center; width: 2.15rem; height: 2.15rem; border: 4px solid #f7f9fc; border-radius: 50%; background: #164194; color: white; font-size: .78rem; font-weight: 800; box-shadow: 0 0 0 1px #164194; }
      .deadline-card { padding: 1rem 1.15rem; border: 1px solid #d9e3f1; border-radius: .6rem; background: white; box-shadow: 0 4px 14px rgba(23, 43, 77, .06); }
      .deadline-meta { color: #164194; font-size: .76rem; font-weight: 800; letter-spacing: .09em; text-transform: uppercase; }
      .deadline-trigger { margin-top: .22rem; color: #172b4d; font-size: 1.18rem; font-weight: 750; }
      .deadline-action { margin-top: .35rem; color: #52627a; font-size: 1rem; }
      .deadline-details { display: flex; flex-wrap: wrap; gap: .45rem 1.4rem; margin-top: .8rem; padding-top: .7rem; border-top: 1px solid #edf1f7; color: #52627a; font-size: .92rem; }
      .deadline-details strong { color: #172b4d; font-weight: 700; }
      @media (max-width: 640px) {
        .deadline-item { gap: .8rem; grid-template-columns: 1.9rem 1fr; }
        .deadline-timeline::before { left: .92rem; }
        .deadline-marker { width: 1.9rem; height: 1.9rem; font-size: .7rem; }
        .deadline-card { padding: .9rem; }
      }
    </style>
    """,
    unsafe_allow_html=True,
)


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
        st.markdown('<div class="app-kicker">European Union mobility service</div>', unsafe_allow_html=True)
        st.markdown('<div class="app-title">EU Data Compass</div>', unsafe_allow_html=True)
        st.caption(
            f"Portugal-hosted instance · Origin fixed to **{data.ORIGIN['name']}** · "
            f"One interface for documents, deadlines and information "
            f"across Europe."
        )
    with right:
        st.markdown(" ")
        st.caption(f"Wallet verified · {', '.join(user.nationalities)}")
        if st.button("Sign out", use_container_width=True):
            _wallet_login().sign_out()
            _reset("country")
            st.rerun()
        if st.button("Start over", use_container_width=True):
            _reset("country")
            st.rerun()


def breadcrumb():
    parts = ["Portugal"]
    if st.session_state.country:
        c = data.get_country(st.session_state.country)
        parts.append(c["name"])
    if st.session_state.intent:
        i = next(x for x in data.INTENTS if x["id"] == st.session_state.intent)
        parts.append(i["name"])
    if st.session_state.subject:
        s = next(x for x in data.SUBJECTS if x["id"] == st.session_state.subject)
        parts.append(s["name"])
    st.markdown(" → ".join(parts))
    st.divider()


# ---------------------------------------------------------------------------
# Step 1 — destination picker
# ---------------------------------------------------------------------------

def step_country():
    st.subheader("Where are you going?")
    st.write("Select a destination country. Search by country name or code.")

    country_options = [None] + [c["code"] for c in data.COUNTRIES]
    selected = st.selectbox(
        "Destination country",
        country_options,
        index=country_options.index(st.session_state.country) if st.session_state.country in country_options else 0,
        format_func=lambda code: "Select a country" if code is None else data.get_country(code)["name"],
    )
    if selected and selected != st.session_state.country:
        st.session_state.country = selected
        _reset("intent")
        st.rerun()

    st.caption("Germany and Spain have verified content. Other destinations currently use draft matrix data.")


# ---------------------------------------------------------------------------
# Step 2 — intent
# ---------------------------------------------------------------------------

def step_intent():
    c = data.get_country(st.session_state.country)
    st.subheader(f"Traveling to {c['name']}, or moving in?")
    cols = st.columns(2)
    for idx, i in enumerate(data.INTENTS):
        with cols[idx]:
            with st.container(border=True):
                st.markdown(f"### {i['name']}")
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
            label = s["name"]
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
            st.markdown("**Inform with ID** — notify your destination (and Portugal) that you are "
                        "traveling, using the EU Digital Identity Wallet.")
            st.caption("Wallet-gated feature. EUDI Wallets become mandatory 24 Dec 2026; production "
                       "wallets land ~2027 (docs/02-spec/EUDI-WALLET.md). Disabled until the wallet layer is wired in.")
        with cols[1]:
            st.button("Inform with ID", disabled=True, use_container_width=True,
                      help="Coming with the EUDI Wallet integration (~2027).")


def deadline_timeline(deadlines):
    """Render deadline milestones as a vertical, date-ordered timeline."""
    items = []
    for index, deadline in enumerate(deadlines, start=1):
        trigger = escape(str(deadline["trigger"]))
        action = escape(str(deadline["action"]))
        window = escape(str(deadline["window"]))
        fine = escape(str(deadline["fine"]))
        items.append(
            f'''<div class="deadline-item">
                  <div class="deadline-marker">{index}</div>
                  <div class="deadline-card">
                    <div class="deadline-meta">Milestone {index}</div>
                    <div class="deadline-trigger">{trigger}</div>
                    <div class="deadline-action">{action}</div>
                    <div class="deadline-details">
                      <span>Time allowed: <strong>{window}</strong></span>
                      <span>Fine / consequence: <strong>{fine}</strong></span>
                    </div>
                  </div>
                </div>'''
        )
    st.markdown(f'<div class="deadline-timeline">{"".join(items)}</div>', unsafe_allow_html=True)


def dashboard():
    c = data.get_country(st.session_state.country)
    intent = st.session_state.intent
    content = data.get_content(c["code"], intent, st.session_state.subject)

    if content is None:
        st.warning("No content available for this combination yet.")
        return

    if not content["verified"]:
        st.warning("**Rough / unverified data.** This destination's long-stay content comes from "
                   "the draft 8-country matrix and has not been verified against primary sources. "
                   "Germany and Spain are the verified cases.")
    else:
        st.success("Verified content — sourced from primary references (see the Information tab).")

    st.info(content["summary"])
    inform_with_id()

    tab_dl, tab_docs, tab_info = st.tabs(["Deadlines", "Documents", "Information"])

    with tab_dl:
        st.markdown("#### The compliance clock")
        st.caption("Milestones are shown in the order they occur, from arrival or move-in onward.")
        deadline_timeline(content["deadlines"])

    with tab_docs:
        st.markdown("#### Documents & forms")
        for doc in content["documents"]:
            with st.expander(doc["name"]):
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
                        st.markdown(f"[Open form / source]({doc['form_url']})")
                with bcols[1]:
                    st.button("Sign with wallet", key=f"sign_{doc['name']}", disabled=True,
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
    st.caption("EU Data Compass prototype · access is protected by the EUDI Wallet verifier service · "
               "content per docs/ · not legal advice.")


if __name__ == "__main__":
    main()
