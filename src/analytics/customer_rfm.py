"""
Customer RFM Segmentation Module (Task DA-06)
Author: Nhóm Thực Hiện (Data & AI Team)
Purpose: Phân khúc khách hàng theo mô hình RFM (Recency, Frequency, Monetary)
Output: data/gold/customer_segments.parquet
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

def compute_customer_rfm(input_path: str, output_path: str) -> None:
    print(f">> [RFM] Dang doc du lieu tu: {input_path}")
    start_time = time.time()
    
    norm_input = Path(input_path).as_posix()
    if os.path.isdir(input_path):
        norm_input = f"{norm_input}/*.parquet"

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    norm_output = Path(output_path).as_posix()

    query = f"""
    COPY (
        WITH user_summary AS (
            SELECT
                user_id,
                MAX(CAST(event_date AS DATE)) AS last_active_date,
                COUNT(DISTINCT user_session) AS frequency,
                COUNT(CASE WHEN event_type = 'purchase' THEN 1 END) AS purchase_count,
                ROUND(COALESCE(SUM(CASE WHEN event_type = 'purchase' THEN price ELSE 0 END), 0), 2) AS monetary
            FROM read_parquet('{norm_input}')
            GROUP BY user_id
        ),
        max_date_cte AS (
            SELECT COALESCE(MAX(last_active_date), DATE '2019-10-31') AS ref_date FROM user_summary
        ),
        rfm_raw AS (
            SELECT
                u.user_id,
                DATE_DIFF('day', u.last_active_date, m.ref_date) AS recency_days,
                u.frequency,
                u.purchase_count,
                u.monetary,
                -- Recency Score (Càng gần ngày mốc điểm càng cao: 1-5)
                CASE 
                    WHEN DATE_DIFF('day', u.last_active_date, m.ref_date) <= 3 THEN 5
                    WHEN DATE_DIFF('day', u.last_active_date, m.ref_date) <= 7 THEN 4
                    WHEN DATE_DIFF('day', u.last_active_date, m.ref_date) <= 14 THEN 3
                    WHEN DATE_DIFF('day', u.last_active_date, m.ref_date) <= 21 THEN 2
                    ELSE 1
                END AS r_score,
                -- Frequency Score (1-5)
                CASE 
                    WHEN u.frequency >= 10 THEN 5
                    WHEN u.frequency >= 5 THEN 4
                    WHEN u.frequency >= 3 THEN 3
                    WHEN u.frequency >= 2 THEN 2
                    ELSE 1
                END AS f_score,
                -- Monetary Score (1-5)
                CASE 
                    WHEN u.monetary >= 1000 THEN 5
                    WHEN u.monetary >= 500 THEN 4
                    WHEN u.monetary >= 200 THEN 3
                    WHEN u.monetary > 0 THEN 2
                    ELSE 1
                END AS m_score
            FROM user_summary u
            CROSS JOIN max_date_cte m
        )
        SELECT
            user_id,
            recency_days,
            frequency,
            purchase_count,
            monetary,
            r_score,
            f_score,
            m_score,
            (r_score * 100 + f_score * 10 + m_score) AS rfm_score,
            CASE
                WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
                WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal Customers'
                WHEN r_score >= 4 AND f_score <= 2 THEN 'Potential Loyalists'
                WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
                WHEN r_score <= 2 AND f_score <= 2 AND monetary > 0 THEN 'Hibernating'
                ELSE 'Lost / Casual Visitors'
            END AS segment
        FROM rfm_raw
        ORDER BY monetary DESC, frequency DESC
    ) TO '{norm_output}' (FORMAT PARQUET, COMPRESSION SNAPPY);
    """
    
    con = duckdb.connect(database=':memory:')
    con.execute(query)
    
    summary_df = con.execute(f"SELECT segment, COUNT(*) as user_count, ROUND(AVG(monetary), 2) as avg_monetary FROM read_parquet('{norm_output}') GROUP BY segment ORDER BY user_count DESC").fetchdf()
    elapsed = time.time() - start_time
    
    print(f">> [RFM] Hoan thanh trong {elapsed:.2f}s!")
    print(f"   * Thong ke cac phan khuc khach hang:")
    for _, row in summary_df.iterrows():
        print(f"     - {row['segment']}: {row['user_count']:,} users (Avg Chi tieu: ${row['avg_monetary']:,.2f})")
    print(f"   * Luu tai: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute Customer RFM Segments")
    parser.add_argument("--sample", action="store_true", help="Chay tren tap sample_100k")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parents[2]
    if args.sample:
        input_data = base_dir / "data" / "silver" / "sample_cleaned_100k.parquet"
    else:
        input_data = base_dir / "data" / "silver" / "events_cleaned.parquet"
        
    output_data = base_dir / "data" / "gold" / "customer_segments.parquet"
    compute_customer_rfm(str(input_data), str(output_data))
