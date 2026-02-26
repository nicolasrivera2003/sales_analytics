import pandas as pd

def clean_sales_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Basic preprocessing:
    - Remove empty rows
    - Normalize column names
    - Convert date columns to datetime
    
    Assumes sales dataset structure similar to Superstore.
    """
    df = df.copy()

    df = df.dropna(how="all")

    # Standardize column names for consistent access
    df.columns = [c.strip().replace(" ", "_").lower() for c in df.columns]

    # Attempt to parse common date columns
    for col in ["order_date", "date", "fecha"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    return df