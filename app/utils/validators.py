def validate_amount(value) -> tuple[bool, str, float]:
    """
    Returns: (ok, message, amount_float)
    """
    try:
        amt = float(value)
    except Exception:
        return False, "Please enter a valid numeric amount.", 0.0

    if amt <= 0:
        return False, "Amount must be greater than 0.", 0.0

    return True, "OK", amt
