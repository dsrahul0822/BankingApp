import pandas as pd
from pathlib import Path

SHEETS = ["login_details", "customers", "transactions"]

def load_all_sheets(excel_path: str) -> dict[str, pd.DataFrame]:
    excel_path = Path(excel_path)
    if not excel_path.exists():
        raise FileNotFoundError(f"Excel DB not found: {excel_path}")

    data = {}
    for s in SHEETS:
        data[s] = pd.read_excel(excel_path, sheet_name=s, engine="openpyxl")
    return data

def save_all_sheets(excel_path: str, sheets: dict[str, pd.DataFrame]) -> None:
    excel_path = Path(excel_path)
    excel_path.parent.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        for name, df in sheets.items():
            df.to_excel(writer, sheet_name=name, index=False)
