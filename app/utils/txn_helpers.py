from datetime import datetime
import pandas as pd

def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def next_txn_id(transactions_df: pd.DataFrame) -> str:
    """
    Generates next txn id like T0000001, T0000002 ...
    """
    if transactions_df.empty or "txn_id" not in transactions_df.columns:
        return "T0000001"

    # Extract numeric part
    ids = transactions_df["txn_id"].astype(str)
    nums = []
    for x in ids:
        x = x.strip()
        if x.startswith("T"):
            x = x[1:]
        if x.isdigit():
            nums.append(int(x))

    if not nums:
        return "T0000001"

    nxt = max(nums) + 1
    return f"T{nxt:07d}"

def add_transaction_row(
    transactions_df: pd.DataFrame,
    customer_id: str,
    account_no: str,
    txn_type: str,
    amount: float,
    balance_after: float,
    channel: str = "ONLINE",
    reference: str = "SELF",
    status: str = "SUCCESS",
    remarks: str = ""
) -> pd.DataFrame:
    txn_id = next_txn_id(transactions_df)

    row = {
        "txn_id": txn_id,
        "customer_id": customer_id,
        "account_no": account_no,
        "txn_ts": now_str(),
        "txn_type": txn_type,
        "amount": amount,
        "balance_after": balance_after,
        "channel": channel,
        "reference": reference,
        "status": status,
        "remarks": remarks
    }

    # Ensure columns exist
    for k in row.keys():
        if k not in transactions_df.columns:
            transactions_df[k] = ""

    return pd.concat([transactions_df, pd.DataFrame([row])], ignore_index=True)
