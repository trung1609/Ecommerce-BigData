"""
DuckDB Interactive Data Explorer
Chay script nay de xem va truy van truc tiep cac bang du lieu Gold bang SQL.
Cach dung:
    python scripts/explore_duckdb.py
"""

import sys
import io
from pathlib import Path
import duckdb

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parents[1]
GOLD_DIR = ROOT_DIR / "data" / "gold"
SILVER_FILE = ROOT_DIR / "data" / "silver" / "sample_cleaned_100k.parquet"

def main():
    con = duckdb.connect(database=":memory:")
    
    # Dang ky tat ca cac file Gold thanh View SQL
    tables = {}
    if GOLD_DIR.exists():
        for p in GOLD_DIR.glob("*.parquet"):
            tname = p.stem
            con.execute(f"CREATE VIEW {tname} AS SELECT * FROM read_parquet('{p.as_posix()}')")
            cnt = con.execute(f"SELECT COUNT(*) FROM {tname}").fetchone()[0]
            tables[tname] = {"path": p, "count": cnt}

    if SILVER_FILE.exists():
        con.execute(f"CREATE VIEW silver_sample AS SELECT * FROM read_parquet('{SILVER_FILE.as_posix()}')")
        cnt = con.execute("SELECT COUNT(*) FROM silver_sample").fetchone()[0]
        tables["silver_sample"] = {"path": SILVER_FILE, "count": cnt}

    print("=" * 65)
    print("      TRINH XEM & TRUY VAN DATABASE DUCKDB (ECOMMERCE)")
    print("=" * 65)
    print("Cac bang du lieu da san sang truy van:")
    for i, (tname, meta) in enumerate(tables.items(), 1):
        print(f"  [{i}] {tname:<25} ({meta['count']:,} ban ghi)")
    print("=" * 65)

    if len(sys.argv) > 1:
        custom_sql = " ".join(sys.argv[1:])
        print(f">> Dang thuc thi: {custom_sql}")
        con.sql(custom_sql).show()
        return

    print("Nhap cau lenh SQL de xem (hoac nhap so 1-6 de xem nhanh 5 dong dau, 'exit' de thoat):")
    tlist = list(tables.keys())

    while True:
        try:
            cmd = input("\nDuckDB> ").strip()
            if not cmd:
                continue
            if cmd.lower() in ["exit", "quit", "q"]:
                print("Tam biet!")
                break
            
            # Neu nhap so thu tu 1, 2, 3...
            if cmd.isdigit() and 1 <= int(cmd) <= len(tlist):
                chosen = tlist[int(cmd) - 1]
                print(f"\n>> Xem 5 dong dau bang '{chosen}':")
                con.sql(f"SELECT * FROM {chosen} LIMIT 5").show()
                continue

            # Thuc thi SQL truc tiep
            con.sql(cmd).show()
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Loi: {e}")

if __name__ == "__main__":
    main()
