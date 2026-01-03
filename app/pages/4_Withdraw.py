import os
import sys
import streamlit as st
from dotenv import load_dotenv

# ✅ Make "app/" import root
APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from utils.data_store import load_all_sheets, save_all_sheets
from utils.session_guard import require_login
from utils.validators import validate_amount
from utils.txn_helpers import add_transaction_row

load_dotenv()

BANK_NAME = os.getenv("BANK_NAME", "State Bank of Python")
DB_EXCEL_PATH = os.getenv("DB_EXCEL_PATH", "data/banking_db.xlsx")

require_login()
customer_id = st.session_state.get("customer_id")

st.title("➖ Withdraw Money")
st.caption(f"{BANK_NAME} • Customer ID: **{customer_id}**")

# Load sheets
sheets = load_all_sheets(DB_EXCEL_PATH)
customers = sheets["customers"]
transactions = sheets["transactions"]

# Get customer row
mask = customers["customer_id"].astype(str) == str(customer_id)
if not mask.any():
    st.error("Customer not found.")
    st.stop()

idx = customers[mask].index[0]
cust = customers.loc[idx].to_dict()

account_no = cust.get("account_no", "")
current_balance = float(cust.get("current_balance", 0.0))

st.info(f"💰 Current Balance: ₹ {current_balance:,.2f}")

st.divider()

with st.form("withdraw_form"):
    amt_in = st.text_input("Enter Withdraw Amount (₹)", placeholder="e.g., 300")
    remarks = st.text_input("Remarks (optional)", placeholder="e.g., ATM / Cash withdraw")
    submitted = st.form_submit_button("Withdraw", type="primary")

if submitted:
    ok, msg, amt = validate_amount(amt_in)
    if not ok:
        st.error(msg)
        st.stop()

    # ✅ Balance check
    if amt > current_balance:
        st.error(f"❌ Insufficient balance. You can withdraw up to ₹ {current_balance:,.2f}")
        st.stop()

    new_balance = current_balance - amt

    # Update customer balance
    customers.loc[idx, "current_balance"] = new_balance

    # Add transaction row
    transactions = add_transaction_row(
        transactions_df=transactions,
        customer_id=str(customer_id),
        account_no=str(account_no),
        txn_type="WITHDRAW",
        amount=float(amt),
        balance_after=float(new_balance),
        channel="ONLINE",
        reference="WITHDRAW",
        status="SUCCESS",
        remarks=str(remarks).strip()
    )

    # Save back
    sheets["customers"] = customers
    sheets["transactions"] = transactions
    save_all_sheets(DB_EXCEL_PATH, sheets)

    st.success(f"✅ Withdrawal successful! Withdrawn ₹ {amt:,.2f}")
    st.info(f"Updated Balance: ₹ {new_balance:,.2f}")

    st.caption("Go to **2_Summary** or **5_Mini_Statement** to verify the transaction.")
