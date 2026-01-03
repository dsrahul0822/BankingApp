import streamlit as st

st.set_page_config(page_title="State Bank of Python", page_icon="🏦", layout="wide")

st.title("🏦 State Bank of Python")

if "is_logged_in" in st.session_state and st.session_state.is_logged_in:
    st.success(f"Logged in as Customer: {st.session_state.get('customer_id')}")
else:
    st.warning("Not logged in. Please login from 🔐 Login page.")
