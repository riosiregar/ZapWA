def normalize_id_phone(s: str) -> str:
    digits = "".join(ch for ch in str(s) if ch.isdigit())
    if digits.startswith("62"):
        p = digits
    elif digits.startswith("0"):
        p = "62" + digits[1:]
    elif digits.startswith("8"):
        p = "62" + digits
    else:
        p = digits
    return f"+{p}"
