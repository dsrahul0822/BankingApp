import os
import sys
import streamlit as st
from dotenv import load_dotenv

# ✅ Make "app/" import root, so we can do: from utils...
APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from utils.data_store import load_all_sheets, save_all_sheets
from utils.auth import authenticate_and_update_plain, unlock_user

load_dotenv()

BANK_NAME = os.getenv("BANK_NAME", "State Bank of Python")
DB_EXCEL_PATH = os.getenv("DB_EXCEL_PATH", "data/banking_db.xlsx")

st.title("🔐 Login")
st.caption(f"Welcome to **{BANK_NAME}**")

# Session defaults
if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False
if "customer_id" not in st.session_state:
    st.session_state.customer_id = None

with st.form("login_form", clear_on_submit=False):
    username = st.text_input("Username", placeholder="rahul / demo")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Login", type="primary")

if submitted:
    try:
        sheets = load_all_sheets(DB_EXCEL_PATH)
        login_df = sheets["login_details"]

        ok, msg, updated_login_df, cust_id = authenticate_and_update_plain(
            login_df=login_df,
            username=username,
            password=password
        )

        sheets["login_details"] = updated_login_df
        save_all_sheets(DB_EXCEL_PATH, sheets)

        if ok:
            st.success(msg)
            st.session_state.is_logged_in = True
            st.session_state.customer_id = cust_id
            st.info("Now open **2_Summary** page from the sidebar ✅")
        else:
            st.error(msg)

    except Exception as e:
        st.exception(e)

st.divider()
st.write("### Session Status")
st.write("Logged in:", st.session_state.is_logged_in)
st.write("Customer ID:", st.session_state.customer_id)

# ✅ Optional: Unlock section (so you don’t need Excel edits)
st.divider()
st.subheader("🔓 Admin Unlock (Demo)")
unlock_name = st.text_input("Unlock username", value=username if username else "")
if st.button("Unlock Account"):
    sheets = load_all_sheets(DB_EXCEL_PATH)
    df = sheets["login_details"]
    ok, df = unlock_user(df, unlock_name)
    if ok:
        sheets["login_details"] = df
        save_all_sheets(DB_EXCEL_PATH, sheets)
        st.success(f"Unlocked: {unlock_name}")
    else:
        st.error("User not found.")
