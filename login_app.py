#login_app.py
import streamlit as st
import os
from eudi_login.client import EUDIWalletLogin

# Configure the client to point to the FastAPI service
# In local dev with docker-compose, this is http://eudi_service:5000
# In local dev without docker, this might be http://localhost:5000
API_BASE_URL = os.environ.get("EUDI_API_URL", "http://localhost:5000")

auth = EUDIWalletLogin(
    api_base_url=API_BASE_URL,
    allowed_nationalities={"SK", "DE", "FR", "NL"},  # Example allow-list
)

st.set_page_config(page_title="Travel Registration", page_icon="✈️")

# --- Authentication Gate ---
if "user" not in st.session_state:
    st.session_state.user = auth.authenticate()

user = st.session_state.user

if user is None or not user.verified:
    st.stop()

# --- Actual Application Starts Here ---
st.title("✈️ Travel Registration")
st.success(f"Authenticated as citizen of: {', '.join(user.nationalities)}")

st.markdown("---")
st.write("Welcome to the secure travel registration portal.")
st.write("Your identity has been cryptographically verified via your EUDI Wallet.")

# ... rest of your app logic ...