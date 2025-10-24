# app/helpers/phone.py
import re
import pandas as pd


def normalize_msisdn(s: str) -> str:
    s = re.sub(r"\D", "", s or "")
    if not s:
        return s
    if s.startswith("0"):
        s = "62" + s[1:]
    if s.startswith("8"):
        s = "62" + s
    return s


def extract_msisdn_from_any(df: pd.DataFrame) -> list[str]:
    # cari pola angka 8–16 digit di semua kolom
    found: list[str] = []
    for col in df.columns:
        series = df[col].astype(str)
        for v in series:
            m = re.findall(r"\b(?:0?\d{9,16}|\d{9,16})\b", v)
            found.extend(m)
    return found
