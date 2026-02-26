import pandas as pd

def load_csv(path: str) -> pd.DataFrame:
    """
    Load CSV data with robust encoding handling.
    
    Many public datasets are not UTF-8 encoded.
    We attempt UTF-8 first, then fallback to latin-1.
    """
    try:
        return pd.read_csv(path, encoding="utf-8")
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="latin-1")