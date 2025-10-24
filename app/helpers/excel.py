import pandas as pd
from io import BytesIO


def read_first_column_as_series(file_bytes: bytes) -> pd.Series:
    df = pd.read_excel(BytesIO(file_bytes), engine="openpyxl")
    col = df.columns[0]
    return df[col].astype(str)
