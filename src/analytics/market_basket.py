"""
Market Basket Analysis & Two-Stage Recommendation Engine
Author: Nhóm Thực Hiện (Data & AI Team)
Purpose: 
  1. Khai phá luật kết hợp ngành hàng (Category Association Rules) từ dữ liệu Silver.
  2. Xuất bảng Gold data/gold/cross_sell_rules.parquet.
  3. Cung cấp hàm gợi ý Two-Stage (Candidate Generation -> Reranking) cho Dashboard.
"""

from pathlib import Path
import time
import numpy as np
import pandas as pd
import duckdb

BASE_DIR = Path(__file__).resolve().parents[2]
SILVER_PATH = BASE_DIR / "data" / "silver" / "sample_cleaned_100k.parquet"
FALLBACK_SILVER_PATH = BASE_DIR / "data" / "silver" / "events_cleaned.parquet"
GOLD_DIR = BASE_DIR / "data" / "gold"
RULES_OUTPUT_PATH = GOLD_DIR / "cross_sell_rules.parquet"


def get_silver_source_path() -> str:
    """Trả về đường dẫn file Silver khả dụng nhất."""
    if SILVER_PATH.exists():
        return SILVER_PATH.as_posix()
    if FALLBACK_SILVER_PATH.exists():
        return FALLBACK_SILVER_PATH.as_posix()
    raise FileNotFoundError("Không tìm thấy file Silver parquet.")


def generate_category_association_rules(
    input_path: str | None = None,
    output_path: str | None = None,
    min_session_count: int = 10,
    min_confidence: float = 1.0,
    min_lift: float = 1.2
) -> pd.DataFrame:
    """
    Khai phá luật kết hợp đồng xuất hiện chuẩn hóa mức session-category.
    Xuất bảng Gold cross_sell_rules.parquet.
    """
    src_file = input_path or get_silver_source_path()
    out_file = Path(output_path or RULES_OUTPUT_PATH)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(database=":memory:")
    t0 = time.time()

    query = f"""
    -- Bước 1: Chuẩn hóa mức (user_session, category_code) duy nhất
    WITH session_cat_summary AS (
        SELECT 
            user_session,
            category_code,
            MAX(CASE 
                WHEN event_type = 'purchase' THEN 5 
                WHEN event_type = 'cart' THEN 3 
                ELSE 1 
            END) AS cat_weight
        FROM '{src_file}'
        WHERE category_code IS NOT NULL 
          AND category_code != '' 
          AND category_code NOT LIKE '%unknown%'
        GROUP BY user_session, category_code
    ),
    -- Bước 2: Tự kết hợp (Self-join) các danh mục khác nhau trong cùng phiên
    cat_pairs AS (
        SELECT 
            a.category_code AS src_cat,
            b.category_code AS tgt_cat,
            COUNT(DISTINCT a.user_session) AS session_co_count,
            SUM(a.cat_weight * b.cat_weight) AS weighted_co_score
        FROM session_cat_summary a
        JOIN session_cat_summary b 
          ON a.user_session = b.user_session 
         AND a.category_code != b.category_code
        GROUP BY a.category_code, b.category_code
    ),
    cat_session_totals AS (
        SELECT category_code, COUNT(DISTINCT user_session) AS total_sessions
        FROM session_cat_summary
        GROUP BY category_code
    ),
    total_distinct_sessions AS (
        SELECT COUNT(DISTINCT user_session) AS total_market_sessions
        FROM session_cat_summary
    )
    SELECT 
        p.src_cat,
        p.tgt_cat,
        p.session_co_count,
        p.weighted_co_score,
        ROUND(p.session_co_count * 100.0 / s.total_sessions, 2) AS confidence_pct,
        ROUND(
            (p.session_co_count * 1.0 / s.total_sessions) / 
            (t.total_sessions * 1.0 / m.total_market_sessions), 
            2
        ) AS lift
    FROM cat_pairs p
    JOIN cat_session_totals s ON p.src_cat = s.category_code
    JOIN cat_session_totals t ON p.tgt_cat = t.category_code
    CROSS JOIN total_distinct_sessions m
    WHERE p.session_co_count >= {min_session_count}
      AND (p.session_co_count * 100.0 / s.total_sessions) >= {min_confidence}
      AND (
          (p.session_co_count * 1.0 / s.total_sessions) / 
          (t.total_sessions * 1.0 / m.total_market_sessions)
      ) >= {min_lift}
    ORDER BY p.src_cat ASC, lift DESC
    """

    df_rules = con.execute(query).fetchdf()
    df_rules.to_parquet(out_file, index=False)
    print(f"Generated category association rules: {out_file} ({len(df_rules)} rules in {time.time()-t0:.2f}s)")
    return df_rules


def get_recommendations_for_product(
    src_product_id: int,
    top_k: int = 3,
    data_path: str | None = None,
    rules_path: str | None = None
) -> tuple[pd.DataFrame, dict]:
    """
    Hàm gợi ý Two-Stage hoàn chỉnh:
      Giai đoạn 1: Lấy thông tin src_product -> Tra luật tìm target_categories (fallback cùng category).
      Giai đoạn 2: Lấy candidates -> Rerank chuẩn hóa trong [0, 1] (Lift, Brand, Price, Popularity).
    """
    src_file = data_path or get_silver_source_path()
    r_file = Path(rules_path or RULES_OUTPUT_PATH)

    con = duckdb.connect(database=":memory:")

    # 1. Tra cứu sản phẩm nguồn
    src_df = con.execute(f"""
        SELECT 
            product_id, 
            category_code, 
            LOWER(COALESCE(brand, 'unknown')) AS brand, 
            price
        FROM '{src_file}'
        WHERE product_id = {src_product_id}
        LIMIT 1
    """).fetchdf()

    if src_df.empty:
        return pd.DataFrame(), {"error": f"Không tìm thấy sản phẩm ID {src_product_id}"}

    src_cat = src_df.iloc[0]['category_code']
    src_brand = src_df.iloc[0]['brand']
    src_price = float(src_df.iloc[0]['price']) if src_df.iloc[0]['price'] else 100.0

    # 2. Tìm danh mục mục tiêu từ bảng luật Gold (nếu file luật chưa có thì tự sinh)
    if not r_file.exists():
        generate_category_association_rules(input_path=src_file, output_path=r_file.as_posix())

    target_cats_df = con.execute(f"""
        SELECT tgt_cat, lift, confidence_pct
        FROM read_parquet('{r_file.as_posix()}')
        WHERE src_cat = '{src_cat}'
        ORDER BY lift DESC
        LIMIT 2
    """).fetchdf()

    # Fallback cơ chế: Nếu không có luật cross-category, gợi ý thay thế cùng category
    if target_cats_df.empty:
        target_cats = [src_cat]
        target_clause = f"'{src_cat}'"
        rule_lift = 1.0
        rec_type = "Sản phẩm thay thế cùng ngành (Substitute)"
        badge_class = "badge-gold"
    else:
        target_cats = target_cats_df['tgt_cat'].tolist()
        target_clause = ", ".join(f"'{c}'" for c in target_cats)
        rule_lift = float(target_cats_df.iloc[0]['lift'])
        rec_type = "Gợi ý mua kèm phụ kiện (Cross-sell Bundle)"
        badge_class = "badge-live"

    # 3. Lấy candidate products
    candidates_sql = f"""
    SELECT 
        product_id,
        category_code,
        LOWER(COALESCE(brand, 'unknown')) AS brand,
        price,
        COUNT(*) AS views,
        SUM(CASE WHEN event_type = 'cart' THEN 1 ELSE 0 END) AS carts,
        SUM(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) AS purchases
    FROM '{src_file}'
    WHERE category_code IN ({target_clause})
      AND product_id != {src_product_id}
      AND price IS NOT NULL AND price > 0
    GROUP BY product_id, category_code, brand, price
    HAVING COUNT(*) >= 1
    """
    cand_df = con.execute(candidates_sql).fetchdf()
    if cand_df.empty:
        return pd.DataFrame(), {"error": "Không có ứng viên phù hợp"}

    # 4. Reranking chuẩn hóa chặt chẽ trong [0, 1]
    # A. Brand affinity: 1.0 nếu cùng hãng, 0.35 nếu khác hãng
    cand_df['brand_score'] = cand_df['brand'].apply(
        lambda b: 1.0 if (b == src_brand and b != 'unknown') else 0.35
    )

    # B. Price compatibility: log-Gaussian quanh mức giá nguồn (sigma=0.6)
    cand_df['price_ratio'] = cand_df['price'] / max(src_price, 1.0)
    cand_df['price_score'] = np.exp(-0.5 * (np.log(cand_df['price_ratio']) / 0.6) ** 2)

    # C. Popularity: Min-Max trên log-activity
    raw_pop = np.log1p(
        cand_df['purchases'] * 5.0 + 
        cand_df['carts'] * 2.0 + 
        cand_df['views'] * 1.0
    )
    p_min, p_max = raw_pop.min(), raw_pop.max()
    cand_df['pop_score'] = (raw_pop - p_min) / (p_max - p_min) if p_max > p_min else 0.5

    # D. Rule Strength
    norm_lift = min(rule_lift / 15.0, 1.0)

    # E. Tổng điểm xếp hạng
    cand_df['rank_score'] = (
        0.20 * norm_lift +
        0.30 * cand_df['brand_score'] +
        0.25 * cand_df['price_score'] +
        0.25 * cand_df['pop_score']
    )

    ranked_recs = cand_df.sort_values(by='rank_score', ascending=False).head(top_k).copy()
    
    metadata = {
        "src_product_id": src_product_id,
        "src_category": src_cat,
        "src_brand": src_brand.upper(),
        "src_price": src_price,
        "target_categories": target_cats,
        "rule_lift": rule_lift,
        "recommendation_type": rec_type,
        "badge_class": badge_class
    }

    return ranked_recs, metadata


CATEGORY_DISPLAY_MAP = {
    "electronics.audio.subwoofer": "Loa trầm ô tô",
    "electronics.smartphone": "Điện thoại",
    "electronics.video.tv": "Tivi Smart",
    "electronics.audio.headphone": "Tai nghe",
    "electronics.clocks": "Đồng hồ thông minh",
    "computers.peripherals.keyboard": "Bàn phím máy tính",
    "computers.peripherals.mouse": "Chuột máy tính",
    "computers.peripherals.monitor": "Màn hình máy tính",
    "computers.notebook": "Laptop",
    "auto.accessories.player": "Đầu phát âm thanh ô tô",
    "auto.accessories.videoregister": "Camera hành trình",
    "auto.accessories.alarm": "Còi báo động ô tô",
    "appliances.kitchen.refrigerators": "Tủ lạnh",
    "appliances.kitchen.washer": "Máy giặt",
    "appliances.environment.air_conditioner": "Điều hòa / Máy lạnh",
    "appliances.environment.vacuum": "Máy hút bụi",
}

VIETNAMESE_SYNONYMS = {
    "bàn phím": "keyboard",
    "ban phim": "keyboard",
    "chuột": "mouse",
    "chuot": "mouse",
    "tai nghe": "headphone",
    "điện thoại": "smartphone",
    "dien thoai": "smartphone",
    "máy tính": "notebook",
    "may tinh": "notebook",
    "laptop": "notebook",
    "loa": "audio",
    "loa trầm": "subwoofer",
    "loa tram": "subwoofer",
    "tivi": "tv",
    "đồng hồ": "watch",
    "dong ho": "watch",
    "tủ lạnh": "refrigerator",
    "tu lanh": "refrigerator",
    "máy giặt": "washer",
    "may giat": "washer",
    "máy hút bụi": "vacuum",
    "may hut bui": "vacuum",
    "điều hòa": "air_conditioner",
    "dieu hoa": "air_conditioner",
    "máy lạnh": "air_conditioner",
    "may lanh": "air_conditioner",
    "camera": "videoregister",
    "màn hình": "monitor",
    "man hinh": "monitor",
}


def format_product_name(product_id: int, category_code: str, brand: str, price: float) -> str:
    """Định dạng tên hiển thị chuyên nghiệp kết hợp ngành hàng và thương hiệu."""
    cat_vn = CATEGORY_DISPLAY_MAP.get(category_code, category_code.split(".")[-1].capitalize() if category_code else "Sản phẩm")
    brand_clean = (brand or "unknown").strip().upper()
    brand_str = brand_clean if brand_clean != "UNKNOWN" else "No-Brand"
    return f"{cat_vn} {brand_str} (${price:.2f}) - ID: {product_id}"


def search_catalog_products(keyword: str, limit: int = 15, data_path: str | None = None) -> list[dict]:
    """
    Tìm kiếm sản phẩm theo tên tiếng Việt/Anh, danh mục, thương hiệu hoặc Product ID.
    Trả về danh sách dict chứa đầy đủ thông tin định dạng để hiển thị trên giao diện.
    """
    keyword = (keyword or "").strip()
    if not keyword:
        return []

    src_file = data_path or get_silver_source_path()
    con = duckdb.connect(database=":memory:")

    # Nếu người dùng nhập trực tiếp ID số
    if keyword.isdigit():
        df = con.execute(f"""
            SELECT 
                product_id, 
                category_code, 
                LOWER(COALESCE(brand, 'unknown')) AS brand, 
                ROUND(price, 2) AS price, 
                COUNT(*) AS events
            FROM '{src_file}'
            WHERE product_id = {int(keyword)}
            GROUP BY product_id, category_code, brand, price
            LIMIT 1
        """).fetchdf()
        if not df.empty:
            item = df.iloc[0].to_dict()
            item['display_name'] = format_product_name(item['product_id'], item['category_code'], item['brand'], item['price'])
            return [item]

    # Nhận diện từ khóa tiếng Việt / tiếng Anh
    kw_lower = keyword.lower()
    search_tokens = [kw_lower]
    for vn, en in VIETNAMESE_SYNONYMS.items():
        if vn in kw_lower:
            search_tokens.append(en)

    clauses = []
    for token in search_tokens:
        clean = token.replace("'", "''")
        clauses.append(f"category_code ILIKE '%{clean}%'")
        clauses.append(f"brand ILIKE '%{clean}%'")

    where_sql = " OR ".join(clauses)

    query = f"""
        SELECT 
            product_id, 
            category_code, 
            LOWER(COALESCE(brand, 'unknown')) AS brand, 
            ROUND(price, 2) AS price, 
            COUNT(*) AS events
        FROM '{src_file}'
        WHERE ({where_sql})
          AND price IS NOT NULL AND price > 0
        GROUP BY product_id, category_code, brand, price
        ORDER BY events DESC
        LIMIT {limit}
    """
    df = con.execute(query).fetchdf()
    if df.empty:
        return []

    results = []
    for _, row in df.iterrows():
        item = row.to_dict()
        item['display_name'] = format_product_name(int(item['product_id']), item['category_code'], item['brand'], float(item['price']))
        results.append(item)

    return results


def get_featured_source_products() -> list[dict]:
    """Trả về danh sách 5 sản phẩm tiêu biểu từ các ngành khác nhau để làm demo trên giao diện."""
    return [
        {"id": 5800808, "name": "Loa trầm ô tô PIONEER ($88.01) - ID: 5800808", "cat": "electronics.audio.subwoofer", "brand": "PIONEER", "price": 88.01},
        {"id": 1004767, "name": "Điện thoại SAMSUNG Galaxy A50 ($254.76) - ID: 1004767", "cat": "electronics.smartphone", "brand": "SAMSUNG", "price": 254.76},
        {"id": 9200581, "name": "Bàn phím máy tính RAPOO ($26.26) - ID: 9200581", "cat": "computers.peripherals.keyboard", "brand": "RAPOO", "price": 26.26},
        {"id": 4804056, "name": "Tai nghe không dây APPLE ($161.93) - ID: 4804056", "cat": "electronics.audio.headphone", "brand": "APPLE", "price": 161.93},
        {"id": 1801690, "name": "Tivi Smart SAMSUNG 4K ($368.04) - ID: 1801690", "cat": "electronics.video.tv", "brand": "SAMSUNG", "price": 368.04},
    ]


if __name__ == "__main__":
    generate_category_association_rules()

