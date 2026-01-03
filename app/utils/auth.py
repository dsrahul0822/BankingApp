from datetime import datetime
import pandas as pd

MAX_ATTEMPTS = 3

def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def _ensure_columns(login_df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure required columns exist. Supports either 'password' or legacy 'password_hash' as plain password.
    """
    if "username" not in login_df.columns:
        login_df["username"] = ""

    # ✅ prefer password, fallback to password_hash (treated as plain)
    if "password" not in login_df.columns:
        if "password_hash" in login_df.columns:
            login_df["password"] = login_df["password_hash"].astype(str)
        else:
            login_df["password"] = ""

    defaults = {
        "customer_id": "",
        "is_locked": 0,
        "failed_attempts": 0,
        "locked_at": "",
        "last_login_at": ""
    }
    for col, default in defaults.items():
        if col not in login_df.columns:
            login_df[col] = default

    return login_df

def authenticate_and_update_plain(
    login_df: pd.DataFrame,
    username: str,
    password: str
) -> tuple[bool, str, pd.DataFrame, str | None]:
    """
    Plain-text authentication.
    Returns: (success, message, updated_login_df, customer_id_if_success)
    """
    username = (username or "").strip()
    password = (password or "").strip()

    login_df = _ensure_columns(login_df)

    if not username or not password:
        return False, "Please enter username and password.", login_df, None

    # Find user
    mask = login_df["username"].astype(str).str.lower() == username.lower()
    if not mask.any():
        return False, "User not found.", login_df, None

    idx = login_df[mask].index[0]

    # Check lock
    if int(login_df.loc[idx, "is_locked"]) == 1:
        return False, "Account is locked. Please contact admin to unlock.", login_df, None

    stored_password = str(login_df.loc[idx, "password"]).strip()

    # ✅ Correct password
    if password == stored_password:
        login_df.loc[idx, "failed_attempts"] = 0
        login_df.loc[idx, "last_login_at"] = now_str()
        return True, "Login successful ✅", login_df, str(login_df.loc[idx, "customer_id"])

    # ❌ Wrong password
    attempts = int(login_df.loc[idx, "failed_attempts"]) + 1
    login_df.loc[idx, "failed_attempts"] = attempts

    if attempts >= MAX_ATTEMPTS:
        login_df.loc[idx, "is_locked"] = 1
        login_df.loc[idx, "locked_at"] = now_str()
        return False, "Account locked ❌ (3 wrong attempts). Contact admin.", login_df, None

    return False, f"Wrong password ❌ Attempts left: {MAX_ATTEMPTS - attempts}", login_df, None

def unlock_user(login_df: pd.DataFrame, username: str) -> tuple[bool, pd.DataFrame]:
    """
    Unlock account (demo/admin utility).
    """
    username = (username or "").strip()
    login_df = _ensure_columns(login_df)

    mask = login_df["username"].astype(str).str.lower() == username.lower()
    if not mask.any():
        return False, login_df

    idx = login_df[mask].index[0]
    login_df.loc[idx, "is_locked"] = 0
    login_df.loc[idx, "failed_attempts"] = 0
    login_df.loc[idx, "locked_at"] = ""
    return True, login_df
