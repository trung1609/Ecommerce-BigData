"""
Category & Brand Performance Analytics Module (Task DA-05)
Author: Nhóm Thực Hiện (Data & AI Team)
Purpose: Thống kê hiệu suất theo ngành hàng (Category) và thương hiệu (Brand), phân tích Pareto 80/20
Output: data/gold/category_brand_stats.parquet
"""

import os
import sys
import time
import argparse
from pathlib import Path
import duckdb

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def compute_category_brand_stats(input_path: str, output_path: str) -> None:
    print(f">> [Brand & Category] Dang doc du lieu tu: {input_path}")
    start_time = time.time()
    
    norm_input = Path(input_path).as_posix()
    if os.path.isdir(input_path):
        norm_input = f"{norm_input}/*.parquet"

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    norm_output = Path(output_path).as_posix()

    query = f"""
    COPY (
        WITH aggregated AS (
            SELECT
                COALESCE(main_category, 'unknown') AS main_category,
                COALESCE(sub_category, 'unknown') AS sub_category,
                COALESCE(brand, 'unknown') AS brand,
                COUNT(CASE WHEN event_type = 'view' THEN 1 END) AS view_count,
                COUNT(CASE WHEN event_type = 'cart' THEN 1 END) AS cart_count,
                COUNT(CASE WHEN event_type = 'purchase' THEN 1 END) AS purchase_count,
                ROUND(COALESCE(SUM(CASE WHEN event_type = 'purchase' THEN price ELSE 0 END), 0), 2) AS total_revenue,
                ROUND(AVG(price), 2) AS avg_price,
                ROUND(MIN(price), 2) AS min_price,
                ROUND(MAX(price), 2) AS max_price
            FROM read_parquet('{norm_input}')
            GROUP BY 
                COALESCE(main_category, 'unknown'),
                COALESCE(sub_category, 'unknown'),
                COALESCE(brand, 'unknown')
        ),
        total_rev AS (
            SELECT SUM(total_revenue) AS grand_total_revenue FROM aggregated
        )
        SELECT
            a.main_category,
            a.sub_category,
            a.brand,
            a.view_count,
            a.cart_count,
            a.purchase_count,
            a.total_revenue,
            a.avg_price,
            a.min_price,
            a.max_price,
            ROUND(CASE WHEN a.view_count > 0 THEN a.purchase_count * 100.0 / a.view_count ELSE 0 END, 2) AS conversion_rate_pct,
            ROUND(CASE WHEN t.grand_total_revenue > 0 THEN a.total_revenue * 100.0 / t.grand_total_revenue ELSE 0 END, 2) AS revenue_share_pct
        FROM aggregated a
        CROSS JOIN total_rev t
        ORDER BY a.total_revenue DESC, a.view_count DESC
    ) TO '{norm_output}' (FORMAT PARQUET, COMPRESSION SNAPPY);
    """
    
    con = duckdb.connect(database=':memory:')
    con.execute(query)
    
    summary_df = con.execute(f"SELECT COUNT(*) as total_combos, SUM(total_revenue) as rev, brand, total_revenue as top_rev FROM read_parquet('{norm_output}') GROUP BY brand, total_revenue ORDER BY total_revenue DESC LIMIT 5").fetchdf()
    elapsed = time.time() - start_time
    
    print(f">> [Brand & Category] Hoan thanh trong {elapsed:.2f}s!")
    print(f"   * Top 5 thuong hieu doanh thu cao nhat:")
    for idx, row in summary_df.iterrows():
        print(f"     {idx+1}. {row['brand'].upper()}: ${row['top_rev']:,.2f}")
    print(f"   * Luu tai: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute Category & Brand Stats")
    parser.add_argument("--sample", action="store_true", help="Chay tren tap sample_100k")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parents[2]
    if args.sample:
        input_data = base_dir / "data" / "silver" / "sample_cleaned_100k.parquet"
    else:
        input_data = base_dir / "data" / "silver" / "events_cleaned.parquet"
        
    output_data = base_dir / "data" / "gold" / "category_brand_stats.parquet"
    compute_category_brand_stats(str(input_data), str(output_data))
