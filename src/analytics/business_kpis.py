"""
Business KPIs Analytics Module (Task DA-03)
Author: Nhóm Thực Hiện (Data & AI Team)
Purpose: Tính toán các chỉ số kinh doanh hàng ngày theo toàn sàn và theo từng ngành hàng (GMV, DAU, Conversion Rate, AOV)
Output: data/gold/kpis_daily.parquet
"""

import os
import sys
import time
import argparse
from pathlib import Path
import duckdb

# Đảm bảo UTF-8 cho Windows console
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def compute_daily_kpis(input_path: str, output_path: str) -> None:
    print(f">> [KPIs] Dang doc du lieu tu: {input_path}")
    start_time = time.time()
    
    norm_input = Path(input_path).as_posix()
    if os.path.isdir(input_path):
        norm_input = f"{norm_input}/*.parquet"

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    norm_output = Path(output_path).as_posix()

    query = f"""
    COPY (
        WITH base AS (
            SELECT
                event_date,
                COALESCE(main_category, 'unknown') AS main_category,
                user_id,
                user_session,
                event_type,
                price
            FROM read_parquet('{norm_input}')
        ),
        daily_cat AS (
            SELECT
                event_date,
                main_category,
                COUNT(*) AS total_events,
                COUNT(DISTINCT user_session) AS total_sessions,
                COUNT(DISTINCT user_id) AS dau,
                COUNT(CASE WHEN event_type = 'view' THEN 1 END) AS view_count,
                COUNT(CASE WHEN event_type = 'cart' THEN 1 END) AS cart_count,
                COUNT(CASE WHEN event_type = 'purchase' THEN 1 END) AS purchase_count,
                ROUND(COALESCE(SUM(CASE WHEN event_type = 'purchase' THEN price ELSE 0 END), 0), 2) AS gmv,
                ROUND(CASE 
                    WHEN COUNT(DISTINCT user_session) > 0 
                    THEN (COUNT(CASE WHEN event_type = 'purchase' THEN 1 END) * 100.0 / COUNT(DISTINCT user_session))
                    ELSE 0 
                END, 3) AS conversion_rate_pct,
                ROUND(CASE 
                    WHEN COUNT(CASE WHEN event_type = 'purchase' THEN 1 END) > 0 
                    THEN (SUM(CASE WHEN event_type = 'purchase' THEN price ELSE 0 END) / COUNT(CASE WHEN event_type = 'purchase' THEN 1 END))
                    ELSE 0 
                END, 2) AS aov
            FROM base
            GROUP BY event_date, main_category
        ),
        daily_all AS (
            SELECT
                event_date,
                'ALL' AS main_category,
                COUNT(*) AS total_events,
                COUNT(DISTINCT user_session) AS total_sessions,
                COUNT(DISTINCT user_id) AS dau,
                COUNT(CASE WHEN event_type = 'view' THEN 1 END) AS view_count,
                COUNT(CASE WHEN event_type = 'cart' THEN 1 END) AS cart_count,
                COUNT(CASE WHEN event_type = 'purchase' THEN 1 END) AS purchase_count,
                ROUND(COALESCE(SUM(CASE WHEN event_type = 'purchase' THEN price ELSE 0 END), 0), 2) AS gmv,
                ROUND(CASE 
                    WHEN COUNT(DISTINCT user_session) > 0 
                    THEN (COUNT(CASE WHEN event_type = 'purchase' THEN 1 END) * 100.0 / COUNT(DISTINCT user_session))
                    ELSE 0 
                END, 3) AS conversion_rate_pct,
                ROUND(CASE 
                    WHEN COUNT(CASE WHEN event_type = 'purchase' THEN 1 END) > 0 
                    THEN (SUM(CASE WHEN event_type = 'purchase' THEN price ELSE 0 END) / COUNT(CASE WHEN event_type = 'purchase' THEN 1 END))
                    ELSE 0 
                END, 2) AS aov
            FROM base
            GROUP BY event_date
        )
        SELECT * FROM (
            SELECT * FROM daily_all
            UNION ALL
            SELECT * FROM daily_cat
        ) u
        ORDER BY event_date ASC, CASE WHEN main_category = 'ALL' THEN 0 ELSE 1 END
    ) TO '{norm_output}' (FORMAT PARQUET, COMPRESSION SNAPPY);
    """
    
    con = duckdb.connect(database=':memory:')
    con.execute(query)
    
    summary_df = con.execute(f"SELECT COUNT(*) as rows, SUM(gmv) as total_gmv, SUM(purchase_count) as total_orders FROM read_parquet('{norm_output}') WHERE main_category = 'ALL'").fetchdf()
    elapsed = time.time() - start_time
    
    print(f">> [KPIs] Hoan thanh trong {elapsed:.2f}s!")
    print(f"   * Tong so ngay (ALL): {summary_df['rows'].iloc[0]}")
    print(f"   * Tong GMV (ALL): ${summary_df['total_gmv'].iloc[0]:,.2f}")
    print(f"   * Tong so don hang (ALL): {summary_df['total_orders'].iloc[0]:,}")
    print(f"   * Luu tai: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute Daily Business KPIs")
    parser.add_argument("--sample", action="store_true", help="Chay tren tap sample_100k")
    parser.add_argument("--full", action="store_true", help="Chay tren toan bo dataset Silver")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parents[2]
    if args.sample:
        input_data = base_dir / "data" / "silver" / "sample_cleaned_100k.parquet"
    else:
        input_data = base_dir / "data" / "silver" / "events_cleaned.parquet"
        
    output_data = base_dir / "data" / "gold" / "kpis_daily.parquet"
    compute_daily_kpis(str(input_data), str(output_data))
