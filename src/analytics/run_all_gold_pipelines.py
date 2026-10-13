"""
Master Gold Pipeline Runner (Task 1.6)
Author: Nhóm Thực Hiện (Data & AI Team)
Purpose: Điều phối chạy toàn bộ 4 pipeline tầng Gold (KPIs, Funnel, Brand/Category, RFM)
Usage:
    python src/analytics/run_all_gold_pipelines.py --sample
    python src/analytics/run_all_gold_pipelines.py --full
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

# Import 4 pipeline functions
from business_kpis import compute_daily_kpis
from funnel_analysis import compute_funnel_metrics
from category_brand_stats import compute_category_brand_stats
from customer_rfm import compute_customer_rfm

def run_all(use_sample: bool = False):
    base_dir = Path(__file__).resolve().parents[2]
    
    if use_sample:
        input_data = base_dir / "data" / "silver" / "sample_cleaned_100k.parquet"
        mode_label = "SAMPLE (100k rows)"
    else:
        input_data = base_dir / "data" / "silver" / "events_cleaned.parquet"
        mode_label = "FULL DATASET (Silver Parquet 16 partitions)"
        
    gold_dir = base_dir / "data" / "gold"
    gold_dir.mkdir(parents=True, exist_ok=True)
    
    kpis_out = gold_dir / "kpis_daily.parquet"
    funnel_out = gold_dir / "funnel_metrics.parquet"
    brand_out = gold_dir / "category_brand_stats.parquet"
    rfm_out = gold_dir / "customer_segments.parquet"
    
    print("=" * 65)
    print(f"🚀 KHOI CHAY TOAN BO PIPELINE TANG GOLD (DATA & BI TEAM)")
    print(f"   Che do: {mode_label}")
    print(f"   Input : {input_data}")
    print(f"   Output: {gold_dir}")
    print("=" * 65)
    
    total_start = time.time()
    
    print("\n[1/4] Chay Pipeline 1: Business Daily KPIs...")
    compute_daily_kpis(str(input_data), str(kpis_out))
    
    print("\n[2/4] Chay Pipeline 2: Funnel Analysis...")
    compute_funnel_metrics(str(input_data), str(funnel_out))
    
    print("\n[3/4] Chay Pipeline 3: Category & Brand Performance...")
    compute_category_brand_stats(str(input_data), str(brand_out))
    
    print("\n[4/4] Chay Pipeline 4: Customer RFM Segmentation...")
    compute_customer_rfm(str(input_data), str(rfm_out))
    
    total_time = time.time() - total_start
    
    print("\n" + "=" * 65)
    print(f"🎉 HOAN THANH XUAT SAC TOAN BO TANG GOLD TRONG {total_time:.2f} GIAY!")
    print("=" * 65)
    
    # In báo cáo tổng hợp file và số dòng
    con = duckdb.connect(database=':memory:')
    files = [
        ("KPIs Daily", kpis_out),
        ("Funnel Metrics", funnel_out),
        ("Category & Brand", brand_out),
        ("Customer RFM", rfm_out)
    ]
    
    print("\nBao cao tong hop cac bang Gold:")
    print(f"{'Ten Bang':<20} | {'Dung Luong':<12} | {'So Dong':<12} | {'Trang Thai'}")
    print("-" * 65)
    for name, fpath in files:
        if fpath.exists():
            size_mb = fpath.stat().st_size / (1024 * 1024)
            count = con.execute(f"SELECT COUNT(*) FROM read_parquet('{fpath.as_posix()}')").fetchone()[0]
            size_str = f"{size_mb:.2f} MB" if size_mb >= 0.01 else f"{fpath.stat().st_size / 1024:.1f} KB"
            print(f"{name:<20} | {size_str:<12} | {count:<12,} | [OK]")
        else:
            print(f"{name:<20} | {'-':<12} | {'-':<12} | [MISSING]")
    print("=" * 65)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Master Gold Pipeline Runner")
    parser.add_argument("--sample", action="store_true", help="Chay tren tap 100k mau")
    parser.add_argument("--full", action="store_true", help="Chay tren toan bo dataset Silver")
    args = parser.parse_args()

    # Mặc định nếu không chỉ định thì chạy --sample, nếu có --full thì chạy full
    use_sample = not args.full
    run_all(use_sample=use_sample)
