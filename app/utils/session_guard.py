import streamlit as st

def require_login():
    """
    Call this at the top of any page that must be protected.
    """
    if not st.session_state.get("is_logged_in", False):
        st.error("You are not logged in. Please login from **1_Login** page.")
        st.stop()

    if not st.session_state.get("customer_id"):
        st.error("Session is missing customer_id. Please login again.")
        st.stop()
