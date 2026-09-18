# eudi_login/client.py
from dataclasses import dataclass
from typing import Optional

import requests
import streamlit as st


@dataclass
class EUDIUser:
    subject: str
    nationalities: list[str]
    verified: bool


class EUDIWalletLogin:
    def __init__(self, api_base_url: str, allowed_nationalities: set[str]):
        self.api_base_url = api_base_url.rstrip("/")
        self.allowed_nationalities = allowed_nationalities

    def authenticate(self) -> Optional[EUDIUser]:
        """
        Render the wallet-login gate and return a verified user once the wallet
        has approved the request.

        The login transaction is retained in ``st.session_state``.  Polling is
        performed by a Streamlit fragment, avoiding a two-minute blocking loop
        that would otherwise make the rest of the UI unresponsive.
        """
        user = st.session_state.get("eudi_user")
        if isinstance(user, EUDIUser) and user.verified:
            return user

        transaction = st.session_state.get("eudi_login_transaction")
        if transaction is None:
            transaction = self._initiate_login()
            if transaction is None:
                self._render_connection_error()
                return None
            st.session_state.eudi_login_transaction = transaction

        self._render_login_page(transaction)

        @st.fragment(run_every="2s")
        def poll_login_status():
            status, payload = self._get_status(transaction["state"])
            if status == "pending":
                st.info("Waiting for wallet scan and approval…")
                return
            if status == "connection_error":
                st.warning("Connection to the EUDI Login Service was lost. Retrying…")
                return

            if status == "verified":
                nationalities = payload.get("nationalities", [])
                if not any(n in self.allowed_nationalities for n in nationalities):
                    st.error("Access denied: your nationality is not permitted for this instance.")
                    return
                st.session_state.eudi_user = EUDIUser(
                    subject=f"user-{transaction['state']}",
                    nationalities=nationalities,
                    verified=True,
                )
                st.session_state.pop("eudi_login_transaction", None)
                st.rerun()

            st.session_state.pop("eudi_login_transaction", None)
            if status == "rejected":
                st.error("Access denied by the identity provider.")
            else:
                st.error(f"Verification failed: {payload.get('error', 'unknown error')}")
            if st.button("Try again", key="eudi_login_retry"):
                st.rerun()

        poll_login_status()
        return None

    @staticmethod
    def _render_page_style() -> None:
        """Apply a small, self-contained visual treatment to the access gate."""
        st.markdown(
            """
            <style>
              .stApp { background: radial-gradient(circle at 10% 0%, #dceaff 0, #f5f8fc 34%, #f8fafc 72%); }
              [data-testid="stMainBlockContainer"] { max-width: 1120px; padding: 3.25rem 2rem 2rem; }
              .eudi-brand { color: #164194; font-size: .78rem; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; }
              .eudi-title { color: #12213f; font-size: clamp(2.4rem, 5vw, 4.6rem); font-weight: 760; line-height: 1.02; letter-spacing: -.055em; margin: .8rem 0 1.2rem; max-width: 37rem; }
              .eudi-lead { color: #45546f; font-size: 1.2rem; line-height: 1.65; max-width: 36rem; }
              .eudi-points { display: grid; gap: .8rem; margin-top: 2.1rem; }
              .eudi-point { color: #243451; font-size: 1.05rem; }
              .eudi-point span { display: inline-flex; align-items: center; justify-content: center; width: 1.6rem; height: 1.6rem; margin-right: .65rem; border: 1px solid #c4d8f6; border-radius: 50%; background: #e8f1ff; color: #164194; font-size: .75rem; font-weight: 800; }
              .eudi-card { padding: 2rem 1.75rem 1.6rem; border: 1px solid rgba(172, 190, 217, .75); border-radius: 1.25rem; background: rgba(255, 255, 255, .88); box-shadow: 0 24px 60px rgba(30, 58, 95, .13); text-align: center; }
              .eudi-card-label { color: #164194; font-size: .72rem; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; }
              .eudi-card-title { color: #12213f; font-size: 1.35rem; font-weight: 750; margin: .45rem 0 .3rem; }
              .eudi-card-copy { color: #61708b; font-size: 1rem; line-height: 1.55; margin: 0 auto 1rem; max-width: 18rem; }
              .eudi-qr { display: block; width: min(100%, 225px); margin: 0 auto 1rem; padding: .6rem; border: 1px solid #d9e2f0; border-radius: .8rem; background: #fff; }
              .eudi-link { color: #164194; font-size: .88rem; font-weight: 700; text-decoration: none; }
              .eudi-link:hover { text-decoration: underline; }
              .eudi-note { display: inline-block; margin-top: 1.2rem; padding: .4rem .7rem; border-radius: 999px; background: #eef4fc; color: #61708b; font-size: .74rem; }
              .eudi-footer { color: #71809a; font-size: .8rem; line-height: 1.5; margin-top: 2.2rem; }
              [data-testid="stStatusWidget"] { display: none; }
              @media (max-width: 640px) {
                [data-testid="stMainBlockContainer"] { padding: 2rem 1rem 1.5rem; }
                .eudi-title { font-size: 2.7rem; }
                .eudi-card { margin-top: 1.25rem; padding: 1.5rem 1rem 1.25rem; }
              }
            </style>
            """,
            unsafe_allow_html=True,
        )

    def _render_login_page(self, transaction: dict) -> None:
        self._render_page_style()
        intro, wallet = st.columns([1.18, 0.82], gap="large")
        with intro:
            st.markdown('<div class="eudi-brand">EU Data Compass · European Union mobility service</div>', unsafe_allow_html=True)
            st.markdown('<div class="eudi-title">Your move across Europe, made simpler.</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="eudi-lead">Access personalised deadlines, documents and official information with a verified EU Digital Identity Wallet.</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                """<div class="eudi-points">
                  <div class="eudi-point"><span>1</span>Scan the secure wallet request</div>
                  <div class="eudi-point"><span>2</span>Approve the identity check in your wallet</div>
                  <div class="eudi-point"><span>3</span>Start planning with confidence</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with wallet:
            st.markdown(
                f'''<div class="eudi-card">
                  <div class="eudi-card-label">Secure identity check</div>
                  <div class="eudi-card-title">Connect your EU wallet</div>
                  <div class="eudi-card-copy">Scan this QR code and approve the request to continue.</div>
                  <img class="eudi-qr" src="data:image/svg+xml;base64,{transaction["qr_code_base64"]}" alt="QR code for the EUDI wallet login request">
                  <a class="eudi-link" href="{transaction['sandbox_link']}" target="_blank" rel="noopener">Open the demo wallet&nbsp; ↗</a>
                  <div class="eudi-note">Same-device testing available</div>
                </div>''',
                unsafe_allow_html=True,
            )

        st.markdown(
            '<div class="eudi-footer">We request only the identity information needed to grant access. Demo verifier — not a production identity service.</div>',
            unsafe_allow_html=True,
        )

    def _render_connection_error(self) -> None:
        self._render_page_style()
        st.markdown('<div class="eudi-brand">EU Data Compass · European Union mobility service</div>', unsafe_allow_html=True)
        st.markdown('<div class="eudi-title">Secure access is getting ready.</div>', unsafe_allow_html=True)
        st.write("We could not reach the EUDI Wallet verifier. Start the verifier service, then try again.")
        if st.button("Retry secure connection", type="primary"):
            st.rerun()

    def sign_out(self) -> None:
        """Remove the current wallet session from the Streamlit browser session."""
        st.session_state.pop("eudi_user", None)
        st.session_state.pop("eudi_login_transaction", None)

    def _initiate_login(self) -> Optional[dict]:
        try:
            response = requests.post(f"{self.api_base_url}/login", timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            st.error(f"Failed to connect to EUDI Login Service: {e}")
            return None

        required_fields = {"state", "qr_code_base64", "sandbox_link"}
        if not required_fields.issubset(data):
            st.error("EUDI Login Service returned an incomplete login request.")
            return None
        return data

    def _get_status(self, state: str) -> tuple[str, dict]:
        try:
            response = requests.get(f"{self.api_base_url}/status/{state}", timeout=5)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException:
            return "connection_error", {}
        return data.get("status", "error"), data
