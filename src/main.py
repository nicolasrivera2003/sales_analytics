"""
Main execution script.

This module:
1. Loads raw sales data
2. Cleans and preprocesses it
3. Performs quarterly comparison analysis
4. Generates executive insights report
5. Exports structured CSV outputs for dashboard consumption
"""

from src.config import RAW_DIR, REPORTS_DIR
from src.load_data import load_csv
from src.cleaning import clean_sales_data
from src.analysis import summary_kpis, sales_by_month
from src.quarterly import (
    add_time_columns,
    get_last_two_quarters,
    kpi_by_quarter,
    compare_quarters,
    contribution_by_group,
)
import matplotlib.pyplot as plt

def main():
    REPORTS_DIR.mkdir(exist_ok=True, parents=True)

    csv_path = RAW_DIR / "Sample-Superstore.csv"

    df = load_csv(str(csv_path))
    df = clean_sales_data(df)

    date_col = "order_date"
    sales_col = "sales"

    kpis = summary_kpis(df, sales_col=sales_col)
    print("KPIs:", kpis)

    
    dfq = add_time_columns(df, date_col=date_col)

    
    quarter_kpis = kpi_by_quarter(dfq, sales_col=sales_col)
    quarter_kpis.to_csv(REPORTS_DIR / "sales_by_quarter.csv", index=False)

    last_two = get_last_two_quarters(dfq)
    if len(last_two) < 2:
        raise ValueError("No hay suficientes trimestres en el dataset para comparar.")

    q_prev, q_last = last_two[0], last_two[1]
    q_compare = compare_quarters(dfq, sales_col=sales_col, q_prev=q_prev, q_last=q_last)

    
    candidate_groups = ["category", "region", "segment", "sub_category", "state", "city"]
    group_cols = [c for c in candidate_groups if c in dfq.columns]

    
    contributions = {}
    for col in group_cols:
        contrib = contribution_by_group(dfq, col, sales_col, q_prev, q_last)
        contrib.to_csv(REPORTS_DIR / f"contribution_{col}.csv", index=False)
        contributions[col] = contrib

    
    insights_path = REPORTS_DIR / "insights.md"
    with open(insights_path, "w", encoding="utf-8") as f:
        f.write("# Executive Insights\n\n")
        f.write(f"## Quarter-over-Quarter Comparison\n")
        f.write(f"- Previous quarter: **{q_compare['q_prev']}**\n")
        f.write(f"- Last quarter: **{q_compare['q_last']}**\n")
        f.write(f"- Sales previous: **{q_compare['prev_sales']:.2f}**\n")
        f.write(f"- Sales last: **{q_compare['last_sales']:.2f}**\n")
        f.write(f"- Difference: **{q_compare['diff']:.2f}**\n")
        if q_compare["pct_change"] is not None:
            f.write(f"- % change: **{q_compare['pct_change']:.2f}%**\n\n")
        else:
            f.write("- % change: **N/A (prev sales = 0)**\n\n")

        if contributions:
            f.write("## What drove the change?\n")
            for col, contrib in contributions.items():
                
                worst = contrib.head(5)
                f.write(f"\n### Biggest contributors by `{col}`\n\n")
                f.write(worst.to_markdown(index=False))
                f.write("\n")
        else:
            f.write("## Segmentation\n\nNo se encontraron columnas típicas (category/region/segment) para segmentar.\n")

    monthly = sales_by_month(df, date_col=date_col, sales_col=sales_col)

    
    plt.figure()
    plt.plot(monthly["year_month"], monthly[sales_col])
    plt.xticks(rotation=45, ha="right")
    plt.title("Sales by Month")
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / "sales_by_month.png")
    plt.close()

    monthly.to_csv(REPORTS_DIR / "sales_by_month.csv", index=False)

    print("Saved reports to:", REPORTS_DIR)

if __name__ == "__main__":
    main()