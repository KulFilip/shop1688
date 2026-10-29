import json
from typing import List, Dict, Any
from db import get_connection
from currency import get_nbp_exchange_rates, calculate_prices

def upsert_products(products: List[Dict[str, Any]], connection_uri: str = None) -> int:
    """
    Saves or updates products in NeonDB.
    """
    if not products:
        return 0

    sql = """
    INSERT INTO products (
        offer_id, category, title_pl, title_ua, description_pl, description_ua,
        weight, dimensions, main_image, images, price_cny, margin, price_pln, price_uah,
        min_order_quantity, in_stock, source_platform, source_url, source_seller, raw_attributes, updated_at
    ) VALUES (
        %(offer_id)s, %(category)s, %(title_pl)s, %(title_ua)s, %(description_pl)s, %(description_ua)s,
        %(weight)s, %(dimensions)s, %(main_image)s, %(images)s, %(price_cny)s, %(margin)s, %(price_pln)s, %(price_uah)s,
        %(min_order_quantity)s, %(in_stock)s, %(source_platform)s, %(source_url)s, %(source_seller)s, %(raw_attributes)s, NOW()
    )
    ON CONFLICT (offer_id) DO UPDATE SET
        title_pl = EXCLUDED.title_pl,
        title_ua = EXCLUDED.title_ua,
        description_pl = EXCLUDED.description_pl,
        description_ua = EXCLUDED.description_ua,
        weight = EXCLUDED.weight,
        dimensions = EXCLUDED.dimensions,
        main_image = EXCLUDED.main_image,
        images = EXCLUDED.images,
        price_cny = EXCLUDED.price_cny,
        margin = EXCLUDED.margin,
        price_pln = EXCLUDED.price_pln,
        price_uah = EXCLUDED.price_uah,
        min_order_quantity = EXCLUDED.min_order_quantity,
        in_stock = EXCLUDED.in_stock,
        source_seller = EXCLUDED.source_seller,
        raw_attributes = EXCLUDED.raw_attributes,
        updated_at = NOW();
    """

    count = 0
    with get_connection(connection_uri) as conn:
        with conn.cursor() as cur:
            for p in products:
                # Prepare JSONB fields
                p_copy = dict(p)
                if isinstance(p_copy.get("images"), list):
                    p_copy["images"] = json.dumps(p_copy["images"])
                if isinstance(p_copy.get("raw_attributes"), dict):
                    p_copy["raw_attributes"] = json.dumps(p_copy["raw_attributes"])
                
                cur.execute(sql, p_copy)
                count += 1
        conn.commit()
    return count

