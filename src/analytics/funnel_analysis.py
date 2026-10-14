"""
Funnel Analysis Analytics Module (Task DA-04)
Author: Nhóm Thực Hiện (Data & AI Team)
Purpose: Phân tích phễu chuyển đổi e-commerce (view -> cart -> purchase) và tỷ lệ rơi rụng (drop-off)
Output: data/gold/funnel_metrics.parquet
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

def compute_funnel_metrics(input_path: str, output_path: str) -> None:
    print(f">> [Funnel] Dang doc du lieu tu: {input_path}")
    start_time = time.time()
    
    norm_input = Path(input_path).as_posix()
    if os.path.isdir(input_path):
        norm_input = f"{norm_input}/*.parquet"

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    norm_output = Path(output_path).as_posix()

    query = f"""
    COPY (
        WITH base_cat AS (
            SELECT
                COALESCE(main_category, 'unknown') AS main_category,
                COUNT(CASE WHEN event_type = 'view' THEN 1 END) AS view_count,
                COUNT(CASE WHEN event_type = 'cart' THEN 1 END) AS cart_count,
                COUNT(CASE WHEN event_type = 'purchase' THEN 1 END) AS purchase_count,
                COUNT(DISTINCT CASE WHEN event_type = 'view' THEN user_session END) AS view_sessions,
                COUNT(DISTINCT CASE WHEN event_type = 'cart' THEN user_session END) AS cart_sessions,
                COUNT(DISTINCT CASE WHEN event_type = 'purchase' THEN user_session END) AS purchase_sessions,
                ROUND(COALESCE(SUM(CASE WHEN event_type = 'purchase' THEN price ELSE 0 END), 0), 2) AS gmv
            FROM read_parquet('{norm_input}')
            GROUP BY COALESCE(main_category, 'unknown')
        ),
        overall AS (
            SELECT
                'ALL' AS main_category,
                SUM(view_count) AS view_count,
                SUM(cart_count) AS cart_count,
                SUM(purchase_count) AS purchase_count,
                SUM(view_sessions) AS view_sessions,
                SUM(cart_sessions) AS cart_sessions,
                SUM(purchase_sessions) AS purchase_sessions,
                ROUND(SUM(gmv), 2) AS gmv
            FROM base_cat
        ),
        combined AS (
            SELECT * FROM overall
            UNION ALL
            SELECT * FROM base_cat
        )
        SELECT
            main_category,
            view_count,
            cart_count,
            purchase_count,
            view_sessions,
            cart_sessions,
            purchase_sessions,
            gmv,
            ROUND(CASE WHEN view_count > 0 THEN cart_count * 100.0 / view_count ELSE 0 END, 2) AS view_to_cart_event_rate_pct,
            ROUND(CASE WHEN cart_count > 0 THEN purchase_count * 100.0 / cart_count ELSE 0 END, 2) AS cart_to_purchase_event_rate_pct,
            ROUND(CASE WHEN view_sessions > 0 THEN cart_sessions * 100.0 / view_sessions ELSE 0 END, 2) AS view_to_cart_rate_pct,
            ROUND(CASE WHEN cart_sessions > 0 THEN purchase_sessions * 100.0 / cart_sessions ELSE 0 END, 2) AS cart_to_purchase_rate_pct,
            ROUND(CASE WHEN view_sessions > 0 THEN purchase_sessions * 100.0 / view_sessions ELSE 0 END, 2) AS overall_conversion_rate_pct,
            ROUND(CASE WHEN view_sessions > 0 THEN GREATEST(0.0, (1.0 - (cart_sessions * 1.0 / view_sessions)) * 100.0) ELSE 0 END, 2) AS view_to_cart_drop_pct,
            ROUND(CASE WHEN cart_sessions > 0 THEN GREATEST(0.0, (1.0 - (purchase_sessions * 1.0 / cart_sessions)) * 100.0) ELSE 0 END, 2) AS cart_to_purchase_drop_pct
        FROM combined
        ORDER BY CASE WHEN main_category = 'ALL' THEN 0 ELSE 1 END, view_sessions DESC
    ) TO '{norm_output}' (FORMAT PARQUET, COMPRESSION SNAPPY);
    """
    
    con = duckdb.connect(database=':memory:')
    con.execute(query)
    
    summary_df = con.execute(f"SELECT * FROM read_parquet('{norm_output}') WHERE main_category = 'ALL'").fetchdf()
    elapsed = time.time() - start_time
    
    print(f">> [Funnel] Hoan thanh trong {elapsed:.2f}s!")
    if not summary_df.empty:
        row = summary_df.iloc[0]
        print(f"   * View Sessions: {row['view_sessions']:,}")
        print(f"   * Cart Sessions: {row['cart_sessions']:,} (Conv: {row['view_to_cart_rate_pct']}%)")
        print(f"   * Purchase Sessions: {row['purchase_sessions']:,}")
        print(f"   * Overall Conversion Rate: {row['overall_conversion_rate_pct']}%")
    print(f"   * Luu tai: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute Funnel Metrics")
    parser.add_argument("--sample", action="store_true", help="Chay tren tap sample_100k")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parents[2]
    if args.sample:
        input_data = base_dir / "data" / "silver" / "sample_cleaned_100k.parquet"
    else:
        input_data = base_dir / "data" / "silver" / "events_cleaned.parquet"
        
    output_data = base_dir / "data" / "gold" / "funnel_metrics.parquet"
    compute_funnel_metrics(str(input_data), str(output_data))
