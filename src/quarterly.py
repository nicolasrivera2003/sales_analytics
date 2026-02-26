import pandas as pd

def add_time_columns(df: pd.DataFrame, date_col: str) -> pd.DataFrame:
    """
    Add year and quarter fields for time-based aggregation.
    """
    out = df.copy()
    out = out.dropna(subset=[date_col])
    out["year"] = out[date_col].dt.year
    out["quarter"] = out[date_col].dt.quarter
    out["year_quarter"] = out["year"].astype(str) + "-Q" + out["quarter"].astype(str)
    return out


def compare_quarters(df: pd.DataFrame, sales_col: str, q_prev: str, q_last: str) -> dict:
    """
    Compare sales between two quarters and compute growth metrics.
    """
    prev_sales = df.loc[df["year_quarter"] == q_prev, sales_col].sum()
    last_sales = df.loc[df["year_quarter"] == q_last, sales_col].sum()

    diff = last_sales - prev_sales
    pct = (diff / prev_sales * 100) if prev_sales != 0 else None

    return {
        "q_prev": q_prev,
        "q_last": q_last,
        "prev_sales": float(prev_sales),
        "last_sales": float(last_sales),
        "diff": float(diff),
        "pct_change": float(pct) if pct is not None else None,
    }