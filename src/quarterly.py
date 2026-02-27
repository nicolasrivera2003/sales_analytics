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

def get_last_two_quarters(df: pd.DataFrame) -> list[str]:
    """
    Return the last two quarters available in the dataset, sorted chronologically.
    Expects a 'year_quarter' column (e.g., '2017-Q4').
    """
    quarters = (
        df["year_quarter"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    # Sort by (year, quarter) to handle chronological order correctly
    def key(q: str):
        year_str, qtr_str = q.split("-Q")
        return (int(year_str), int(qtr_str))

    quarters_sorted = sorted(quarters, key=key)
    return quarters_sorted[-2:]

def kpi_by_quarter(df: pd.DataFrame, sales_col: str) -> pd.DataFrame:
    """
    Aggregate total sales by quarter.
    Expects a 'year_quarter' column (e.g., '2017-Q4').
    Output is sorted chronologically.
    """
    out = (
        df.groupby("year_quarter", as_index=False)[sales_col]
        .sum()
        .rename(columns={sales_col: "sales"})
    )

    # Sort using (year, quarter) to avoid lexicographic issues
    def key(q: str):
        year_str, qtr_str = q.split("-Q")
        return (int(year_str), int(qtr_str))

    out["_sort"] = out["year_quarter"].astype(str).map(key)
    out = out.sort_values("_sort").drop(columns=["_sort"]).reset_index(drop=True)
    return out


def contribution_by_group(
    df: pd.DataFrame,
    group_col: str,
    sales_col: str,
    q_prev: str,
    q_last: str,
) -> pd.DataFrame:
    """
    Compute quarter-over-quarter contribution by a segmentation column (e.g., category/region).

    Returns a table:
    group | prev_sales | last_sales | diff | pct_change
    Sorted by diff ascending by default (most negative first).
    """
    prev = (
        df.loc[df["year_quarter"] == q_prev]
        .groupby(group_col, as_index=False)[sales_col]
        .sum()
        .rename(columns={sales_col: "prev_sales"})
    )

    last = (
        df.loc[df["year_quarter"] == q_last]
        .groupby(group_col, as_index=False)[sales_col]
        .sum()
        .rename(columns={sales_col: "last_sales"})
    )

    out = prev.merge(last, on=group_col, how="outer").fillna(0.0)
    out["diff"] = out["last_sales"] - out["prev_sales"]
    out["pct_change"] = out.apply(
        lambda r: (r["diff"] / r["prev_sales"] * 100) if r["prev_sales"] != 0 else None,
        axis=1,
    )

    out = out.sort_values("diff").reset_index(drop=True)
    return out