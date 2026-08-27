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
                return None
            st.session_state.eudi_login_transaction = transaction

        st.markdown("### 🛂 Sign in with your EU Digital Identity Wallet")
        st.write("Scan the QR code with your wallet and approve the identity request to continue.")
        st.image(f"data:image/png;base64,{transaction['qr_code_base64']}", width=250)
        st.markdown(
            f"[Open in EUDI Dev Wallet sandbox]({transaction['sandbox_link']}) "
            "(for same-device testing)"
        )

        @st.fragment(run_every="2s")
        def poll_login_status():
            status, payload = self._get_status(transaction["state"])
            if status == "pending":
                st.info("⏳ Waiting for wallet scan and approval…")
                return
            if status == "connection_error":
                st.warning("Connection to the EUDI Login Service was lost. Retrying…")
                return

            if status == "verified":
                nationalities = payload.get("nationalities", [])
                if not any(n in self.allowed_nationalities for n in nationalities):
                    st.error("⛔ Access denied: your nationality is not permitted for this instance.")
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
                st.error("⛔ Access denied by the identity provider.")
            else:
                st.error(f"⚠️ Verification failed: {payload.get('error', 'unknown error')}")
            if st.button("Try again", key="eudi_login_retry"):
                st.rerun()

        poll_login_status()
        return None

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
