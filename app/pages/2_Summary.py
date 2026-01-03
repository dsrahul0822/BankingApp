import os
import sys
import streamlit as st
from dotenv import load_dotenv

# ✅ Make "app/" import root (so we can do: from utils...)
APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from utils.data_store import load_all_sheets
from utils.session_guard import require_login

load_dotenv()

BANK_NAME = os.getenv("BANK_NAME", "State Bank of Python")
DB_EXCEL_PATH = os.getenv("DB_EXCEL_PATH", "data/banking_db.xlsx")
LOGO_PATH = os.path.join("assets", "sbp_logo.png")  # as per your structure

require_login()

customer_id = st.session_state.get("customer_id")

# Header with logo
col1, col2 = st.columns([1, 3])
with col1:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, use_container_width=True)
    else:
        st.write("🏦")
with col2:
    st.title("📋 Customer Summary")
    st.caption(f"{BANK_NAME} • Logged in Customer ID: **{customer_id}**")

# Load data
sheets = load_all_sheets(DB_EXCEL_PATH)
customers = sheets["customers"]
transactions = sheets["transactions"]

# Fetch customer row
cust = customers[customers["customer_id"].astype(str) == str(customer_id)]
if cust.empty:
    st.error("Customer not found in customers table.")
    st.stop()

cust = cust.iloc[0].to_dict()

# Balance
balance = cust.get("current_balance", 0.0)

# KPI cards
k1, k2, k3 = st.columns(3)
k1.metric("Account No", cust.get("account_no", "NA"))
k2.metric("Account Type", cust.get("account_type", "NA"))
k3.metric("Current Balance (₹)", f"{float(balance):,.2f}")

st.divider()

# Demographic details
st.subheader("👤 Customer Details")

left, right = st.columns(2)

with left:
    st.write(f"**Customer ID:** {cust.get('customer_id', 'NA')}")
    st.write(f"**Full Name:** {cust.get('full_name', 'NA')}")
    st.write(f"**DOB:** {cust.get('dob', 'NA')}")
    st.write(f"**Gender:** {cust.get('gender', 'NA')}")
    st.write(f"**Phone:** {cust.get('phone', 'NA')}")
    st.write(f"**Email:** {cust.get('email', 'NA')}")

with right:
    st.write(f"**KYC Status:** {cust.get('kyc_status', 'NA')}")
    st.write(f"**Account Status:** {cust.get('account_status', 'NA')}")
    st.write(f"**Created At:** {cust.get('created_at', 'NA')}")
    addr = f"{cust.get('address_line1','')}, {cust.get('city','')}, {cust.get('state','')} - {cust.get('pincode','')}"
    st.write("**Address:**")
    st.write(addr.strip(", "))

st.divider()

# Recent transactions preview
st.subheader("🧾 Recent Transactions (Preview)")

tx = transactions[transactions["customer_id"].astype(str) == str(customer_id)].copy()

if tx.empty:
    st.info("No transactions found for this customer.")
else:
    # Sort by timestamp desc if available
    if "txn_ts" in tx.columns:
        tx["txn_ts"] = tx["txn_ts"].astype(str)
        tx = tx.sort_values(by="txn_ts", ascending=False)

    show_cols = [c for c in ["txn_ts", "txn_type", "amount", "balance_after", "status", "remarks"] if c in tx.columns]
    st.dataframe(tx[show_cols].head(10), use_container_width=True)

st.divider()

# Logout button
if st.button("🚪 Logout"):
    st.session_state.is_logged_in = False
    st.session_state.customer_id = None
    st.success("Logged out successfully.")
    st.info("Go back to **1_Login** page to login again.")
