"""
 EU Data Compass
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
import re
import secrets
import sys
from datetime import date, datetime, timedelta
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
      .wallet-status { display: inline-block; margin: .1rem 0 .75rem; padding: .3rem .6rem; border-radius: .35rem; background: #edf7f1; color: #17623a; font-size: .86rem; font-weight: 700; }
      .wallet-status.pending { background: #f1f4f8; color: #52627a; }
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
    st.session_state.setdefault("travel_purpose", None)
    st.session_state.setdefault("travel_context", None)
    st.session_state.setdefault("wallet_documents", set())
    st.session_state.setdefault("inform_stage", "draft")
    st.session_state.setdefault("inform_draft", None)
    st.session_state.setdefault("travel_notification", None)


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
    if to_step in ("country", "intent"):
        st.session_state.travel_purpose = None
        st.session_state.travel_context = None


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
            st.session_state.wallet_documents.clear()
            st.session_state.travel_notification = None
            st.session_state.inform_draft = None
            st.session_state.inform_stage = "draft"
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
    if st.button("Try the Berlin conference demo", key="berlin_conference_demo", use_container_width=True):
        start = date.today()
        end = start + timedelta(days=21)
        st.session_state.country = "DE"
        st.session_state.intent = "traveling"
        st.session_state.subject = "residence"
        st.session_state.travel_purpose = "business"
        st.session_state.travel_context = {
            "city": "Berlin",
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "duration_days": 21,
        }
        st.rerun()


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
    if st.session_state.country == "DE" and st.session_state.intent == "traveling":
        st.subheader("Tell us about your trip")
        st.write("We use this information to tailor the Germany short-stay guidance. It does not create a legal registration.")
        with st.form("germany_travel_context"):
            purpose = st.selectbox(
                "Purpose of travel",
                data.TRAVEL_PURPOSES,
                format_func=lambda item: f'{item["name"]} — {item["description"]}',
            )
            city = st.text_input("Destination city", value="Berlin", placeholder="Berlin")
            start_date = st.date_input("Travel starts", value=date.today(), min_value=date.today())
            end_date = st.date_input("Travel ends", value=date.today() + timedelta(days=21), min_value=date.today())
            submitted = st.form_submit_button("Show my Germany travel plan", type="primary", use_container_width=True)
        if submitted:
            if not city.strip():
                st.error("Enter a destination city.")
            elif end_date < start_date:
                st.error("Travel end date must be on or after the start date.")
            else:
                st.session_state.travel_purpose = purpose["id"]
                st.session_state.travel_context = {
                    "city": city.strip(),
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "duration_days": (end_date - start_date).days + 1,
                }
                st.session_state.subject = "residence"
                st.rerun()
        return

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
    """Render the prototype travel-notification flow."""
    destination = data.get_country(st.session_state.country)
    notification = st.session_state.travel_notification

    with st.container(border=True):
        st.markdown("### Inform with ID")
        if notification and notification["destination_country"] != destination["code"]:
            existing_destination = data.get_country(notification["destination_country"])["name"]
            st.info(f"You already have an active travel notification for {existing_destination}. Delete it before creating a notification for {destination['name']}.")
            if st.button("Delete existing travel notification", key="delete_existing_travel_notification"):
                st.session_state.travel_notification = None
                st.session_state.inform_draft = None
                st.session_state.inform_stage = "draft"
                st.rerun()
            return

        if notification:
            st.success("Travel notification registered with the origin-country registry.")
            details = [
                ("Reference", notification["reference"]),
                ("Destination", data.get_country(notification["destination_country"])["name"]),
                ("Travel period", f'{notification["travel_start"]} to {notification["travel_end"]}'),
                ("Data retained until", notification["retention_until"]),
                ("Contact channels", "Phone and app push" if notification["push_enabled"] else "Phone"),
            ]
            st.table(dict(details))
            st.caption("Prototype record stored in this browser session. No authority or messaging service has been contacted.")
            if st.button("Delete travel notification", key="delete_travel_notification"):
                st.session_state.travel_notification = None
                st.session_state.inform_draft = None
                st.session_state.inform_stage = "draft"
                st.rerun()
            return

        st.write("Notify Portugal that you will be travelling to the selected destination. This helps establish a verified record for future assistance.")
        st.caption("Prototype flow: your destination, dates and contact details are reviewed before simulated EU Wallet approval. Precise location is not requested.")

        if st.session_state.inform_stage == "draft":
            if st.button("Start travel notification", key="start_travel_notification", type="primary", use_container_width=True):
                st.session_state.inform_stage = "form"
                st.rerun()
            return

        if st.session_state.inform_stage == "form":
            existing_draft = st.session_state.inform_draft or {}
            with st.form("travel_notification_form"):
                start_date = st.date_input(
                    "Travel starts",
                    value=date.fromisoformat(existing_draft["travel_start"]) if existing_draft.get("travel_start") else date.today(),
                    min_value=date.today(),
                )
                end_date = st.date_input(
                    "Travel ends",
                    value=date.fromisoformat(existing_draft["travel_end"]) if existing_draft.get("travel_end") else date.today() + timedelta(days=7),
                    min_value=date.today(),
                )
                phone_number = st.text_input(
                    "Phone number for emergency SMS fallback",
                    value=existing_draft.get("phone_number", ""),
                    placeholder="+351 900 000 000",
                )
                push_enabled = st.checkbox("Enable app push notifications", value=existing_draft.get("push_enabled", True))
                submitted = st.form_submit_button("Review notification", type="primary", use_container_width=True)

            if submitted:
                phone = phone_number.strip()
                if end_date < start_date:
                    st.error("Travel end date must be on or after the start date.")
                elif not re.fullmatch(r"\+?[0-9][0-9\s().-]{6,19}", phone):
                    st.error("Enter a valid phone number, including the country code.")
                else:
                    st.session_state.inform_draft = {
                        "origin_country": data.ORIGIN["code"],
                        "destination_country": destination["code"],
                        "travel_start": start_date.isoformat(),
                        "travel_end": end_date.isoformat(),
                        "phone_number": phone,
                        "push_enabled": push_enabled,
                    }
                    st.session_state.pop("inform_retention_until", None)
                    st.session_state.inform_stage = "consent_review"
                    st.rerun()
            return

        if st.session_state.inform_stage == "wallet_approval":
            st.info("The wallet has received a request to approve this travel notification.")
            st.markdown("#### Confirm in your EU Wallet")
            st.write("This demo simulates the user approving the notification with the verified wallet session.")
            if st.button("Confirm in EU Wallet (demo)", key="confirm_wallet_travel_notification", type="primary", use_container_width=True):
                draft = st.session_state.inform_draft
                end = date.fromisoformat(draft["travel_end"])
                retention = st.session_state.get("inform_retention_until", end + timedelta(days=30))
                st.session_state.travel_notification = {
                    "reference": f'PT-{secrets.token_hex(4).upper()}',
                    "subject": st.session_state.eudi_user.subject,
                    "origin_country": draft["origin_country"],
                    "destination_country": draft["destination_country"],
                    "travel_start": draft["travel_start"],
                    "travel_end": draft["travel_end"],
                    "phone_number": draft["phone_number"],
                    "push_enabled": draft["push_enabled"],
                    "retention_until": retention.isoformat(),
                    "consented_at": datetime.now().isoformat(timespec="seconds"),
                    "status": "registered",
                }
                st.session_state.inform_draft = None
                st.session_state.inform_stage = "registered"
                st.rerun()
            return

        draft = st.session_state.inform_draft
        if not draft:
            st.session_state.inform_stage = "draft"
            st.rerun()

        start = date.fromisoformat(draft["travel_start"])
        end = date.fromisoformat(draft["travel_end"])
        default_retention = end + timedelta(days=30)
        retention_until = st.date_input(
            "Keep notification until",
            value=default_retention,
            min_value=end,
            max_value=default_retention,
            key="inform_retention_until",
            help="The default is 30 days after travel ends. You may shorten this period.",
        )
        st.markdown("#### Review before wallet approval")
        st.table({
            "Information": ["Origin country", "Destination", "Travel period", "Phone number", "App push", "Retention"],
            "Value": [
                data.ORIGIN["name"],
                destination["name"],
                f"{start.isoformat()} to {end.isoformat()}",
                draft["phone_number"],
                "Enabled" if draft["push_enabled"] else "Disabled",
                retention_until.isoformat(),
            ],
        })
        st.warning("By continuing, you consent to this prototype sharing the information above with the Portugal origin-country registry. The destination country is recorded as the intended destination but is not contacted in this prototype.")
        review_cols = st.columns(2)
        with review_cols[0]:
            if st.button("Back and edit", key="edit_travel_notification", use_container_width=True):
                st.session_state.pop("inform_retention_until", None)
                st.session_state.inform_stage = "form"
                st.rerun()
        with review_cols[1]:
            if st.button("Approve with EU Wallet (demo)", key="approve_travel_notification", type="primary", use_container_width=True):
                st.session_state.inform_stage = "wallet_approval"
                st.rerun()
        return

def deadline_timeline(deadlines):
    """Render deadline milestones as a vertical, date-ordered timeline."""
    items = []
    for index, deadline in enumerate(deadlines, start=1):
        trigger = escape(str(deadline["trigger"]))
        action = escape(str(deadline["action"]))
        window = escape(str(deadline["window"]))
        fine = escape(str(deadline["fine"]))
        source = ""
        if deadline.get("source_url"):
            source = f'<span>Source: <a href="{escape(deadline["source_url"])}" target="_blank">{escape(deadline.get("source_label", "Official source"))}</a></span>'
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
                      {source}</div>
                  </div>
                </div>'''
        )
    st.markdown(f'<div class="deadline-timeline">{"".join(items)}</div>', unsafe_allow_html=True)


def wallet_document_action(doc):
    """Prototype wallet action; replace with a real issuer flow later."""
    document_name = doc["name"]
    if document_name in st.session_state.wallet_documents:
        st.markdown('<div class="wallet-status">Available in this session’s wallet</div>', unsafe_allow_html=True)
        st.caption("Demo credential only. A production version would be issued by the relevant authority.")
        return

    st.markdown('<div class="wallet-status pending">Not yet available in wallet</div>', unsafe_allow_html=True)
    if st.button(
        "Add to EU Wallet (demo)",
        key=f"wallet_{document_name}",
        use_container_width=True,
        help="Simulates an authority issuing this document to the wallet.",
    ):
        st.session_state.wallet_documents.add(document_name)
        st.rerun()


def dashboard():
    c = data.get_country(st.session_state.country)
    intent = st.session_state.intent
    content = data.get_content(
        c["code"],
        intent,
        st.session_state.subject,
        travel_purpose=st.session_state.travel_purpose,
        travel_context=st.session_state.travel_context,
    )

    if content is None:
        st.warning("No content available for this combination yet.")
        return

    if not content["verified"]:
        st.warning("**Rough / unverified data.** This destination's long-stay content comes from "
                   "the draft 8-country matrix and has not been verified against primary sources. "
                   "Germany and Spain are the verified cases.")
    else:
        st.success("Verified content — sourced from primary references (see the Information tab).")

    if content.get("demo_title"):
        st.markdown(f'### {content["demo_title"]}')
        st.caption(f'Travel purpose: {content["demo_purpose"]}')
    st.info(content["summary"])
    if c["code"] == "DE" and intent == "traveling":
        st.success("You are ready to travel: keep your valid Portuguese ID or passport with you. No German residence registration is required for this temporary-visit scenario.")
    inform_with_id()

    tab_dl, tab_docs, tab_info = st.tabs(["Deadlines", "Documents", "Information"])

    with tab_dl:
        st.markdown("#### The compliance clock")
        st.caption("Milestones are shown in the order they occur, from arrival or move-in onward.")
        deadline_timeline(content["deadlines"])

    with tab_docs:
        st.markdown("#### Documents & forms")
        status_sections = [
            ("required", "Required for this scenario"),
            ("recommended", "Recommended"),
            ("optional", "Optional"),
            ("not_required", "Not required for this scenario"),
        ]
        for status, heading in status_sections:
            docs = [doc for doc in content["documents"] if doc.get("required", "required") == status]
            if not docs:
                continue
            st.markdown(f"#### {heading}")
            for doc in docs:
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
                    if doc.get("source_url"):
                        st.markdown(f'**Official source:** [{doc.get("source_label", "View source")}]({doc["source_url"]})')
                    wallet_document_action(doc)
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
        info_rows = []
        for item in content["info"]:
            if isinstance(item, dict):
                info_rows.append({"Rule": item["label"], "Value": item["value"], "Source": item["source_label"]})
            else:
                info_rows.append({"Rule": item[0], "Value": item[1], "Source": item[2]})
        st.dataframe(info_rows, use_container_width=True, hide_index=True)
        for item in content["info"]:
            if isinstance(item, dict):
                st.markdown(f'[{item["label"]}: official source]({item["source_url"]})')
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
