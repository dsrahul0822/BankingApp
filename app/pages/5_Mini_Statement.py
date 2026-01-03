import os
import sys
import streamlit as st
from dotenv import load_dotenv

# ✅ Make "app/" import root
APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from utils.data_store import load_all_sheets
from utils.session_guard import require_login
from utils.pdf_export import build_mini_statement_pdf

load_dotenv()

BANK_NAME = os.getenv("BANK_NAME", "State Bank of Python")
DB_EXCEL_PATH = os.getenv("DB_EXCEL_PATH", "data/banking_db.xlsx")
LOGO_PATH = os.path.join("assets", "sbp_logo.png")

require_login()
customer_id = st.session_state.get("customer_id")

st.title("🧾 Mini Statement")
st.caption(f"{BANK_NAME} • Customer ID: **{customer_id}**")

# Load data
sheets = load_all_sheets(DB_EXCEL_PATH)
customers = sheets["customers"]
transactions = sheets["transactions"]

# Fetch customer
cust_df = customers[customers["customer_id"].astype(str) == str(customer_id)]
if cust_df.empty:
    st.error("Customer not found in customers table.")
    st.stop()

customer = cust_df.iloc[0].to_dict()

st.divider()

# Controls
col1, col2 = st.columns([1, 1])
with col1:
    n = st.selectbox("Show last N transactions", [5, 10, 15, 20, 50], index=1)
with col2:
    st.write("")
    st.write("")
    show_all = st.checkbox("Show all transactions", value=False)

# Filter transactions
tx = transactions[transactions["customer_id"].astype(str) == str(customer_id)].copy()

if tx.empty:
    st.info("No transactions found for this customer.")
    st.stop()

# Sort by txn_ts desc if present
if "txn_ts" in tx.columns:
    tx["txn_ts"] = tx["txn_ts"].astype(str)
    tx = tx.sort_values(by="txn_ts", ascending=False)

tx_view = tx if show_all else tx.head(int(n))

# Display mini statement
show_cols = [c for c in ["txn_ts", "txn_id", "txn_type", "amount", "balance_after", "status", "remarks"] if c in tx_view.columns]
st.dataframe(tx_view[show_cols], use_container_width=True)

st.divider()

# Download PDF
pdf_bytes = build_mini_statement_pdf(
    bank_name=BANK_NAME,
    customer=customer,
    transactions_df=tx_view[show_cols],
    logo_path=LOGO_PATH
)

file_name = f"{customer.get('customer_id','CUST')}_mini_statement.pdf"

st.download_button(
    label="⬇️ Download Mini Statement (PDF)",
    data=pdf_bytes,
    file_name=file_name,
    mime="application/pdf"
)

st.caption("Tip: Deposit/Withdraw and come back here to see updated entries.")
