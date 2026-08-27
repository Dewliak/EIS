# eudi_login/client.py
import time
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
        Initiates the login flow, displays the QR code, polls for completion,
        and returns a typed EUDIUser object or None if failed/cancelled.
        """
        # 1. Initiate login
        try:
            response = requests.post(f"{self.api_base_url}/login", timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            st.error(f"Failed to connect to EUDI Login Service: {e}")
            return None

        state = data["state"]
        qr_base64 = data["qr_code_base64"]
        sandbox_link = data["sandbox_link"]

        # 2. Display QR Code in Streamlit
        st.markdown("### 🛂 Sign in with your EU Digital Identity Wallet")
        st.image(f"data:image/png;base64,{qr_base64}", width=250)
        st.markdown(f"[Open in EUDI Dev Wallet sandbox]({sandbox_link}) (for same-device testing)")

        status_placeholder = st.empty()

        # 3. Poll for status
        max_attempts = 60  # 2 minutes max
        for _ in range(max_attempts):
            time.sleep(2)
            try:
                status_resp = requests.get(f"{self.api_base_url}/status/{state}", timeout=5)
                status_resp.raise_for_status()
                status_data = status_resp.json()
            except requests.RequestException:
                status_placeholder.warning("Connection to login service lost. Retrying...")
                continue

            status = status_data.get("status")

            if status == "pending":
                status_placeholder.info("⏳ Waiting for wallet scan and approval...")
                continue

            if status == "verified":
                nationalities = status_data.get("nationalities", [])
                # Clear the QR code UI
                status_placeholder.empty()

                # Authorization policy check
                if not any(n in self.allowed_nationalities for n in nationalities):
                    st.error(f"⛔ Access denied. Nationalities {nationalities} are not on the allow-list.")
                    return None

                st.success(f"✅ Identity verified! Welcome.")
                return EUDIUser(
                    subject=f"user-{state}",  # In production, extract sub from VP token
                    nationalities=nationalities,
                    verified=True
                )

            if status == "rejected":
                status_placeholder.empty()
                st.error("⛔ Access denied by the identity provider.")
                return None

            if status == "error":
                status_placeholder.empty()
                st.error(f"⚠️ Verification failed: {status_data.get('error')}")
                return None

        status_placeholder.error("⏱️ Login timed out. Please try again.")
        return None