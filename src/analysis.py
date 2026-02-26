import pandas as pd

def sales_by_month(df: pd.DataFrame, date_col: str, sales_col: str) -> pd.DataFrame:
    """
    Aggregate total sales by month.
    Used for trend visualization in dashboard.
    """
    temp = df.dropna(subset=[date_col]).copy()
    temp["year_month"] = temp[date_col].dt.to_period("M").astype(str)

    return (
        temp.groupby("year_month", as_index=False)[sales_col]
        .sum()
        .sort_values("year_month")
    )


def summary_kpis(df: pd.DataFrame, sales_col: str) -> dict:
    """
    Compute high-level KPIs for executive summary.
    """
    return {
        "rows": int(len(df)),
        "total_sales": float(df[sales_col].sum()),
        "avg_sales": float(df[sales_col].mean()),
    }