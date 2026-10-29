import pytest
from product_sync import upsert_products
from db import get_connection

def test_upsert_product_integration():
    sample = [{
        "offer_id": "test_powerbank_001",
        "category": "power bank",
        "title_pl": "Powerbank 20000mAh Szybkie Ładowanie 22.5W",
        "title_ua": "Повербанк 20000mAh Швидка Зарядка 22.5W",
        "description_pl": "Wysokiej jakości powerbank o pojemności 20000mAh z wyświetlaczem LED.",
        "description_ua": "Високоякісний повербанк ємністю 20000mAh зі світлодіодним дисплеєм.",
        "weight": "420g",
        "dimensions": "142 x 68 x 28 mm",
        "main_image": "https://cbu01.alicdn.com/img/ibank/O1CN01powerbank1.jpg",
        "images": ["https://cbu01.alicdn.com/img/ibank/O1CN01powerbank1.jpg"],
        "price_cny": 45.0,
        "margin": 0.30,
        "price_pln": 34.66,
        "price_uah": 399.77,
        "min_order_quantity": 1,
        "in_stock": True,
        "source_platform": "1688",
        "source_url": "https://detail.1688.com/offer/6789123456.html",
        "source_seller": "Shenzhen Battery Factory Ltd",
        "raw_attributes": {"capacity": "20000mAh", "output": "22.5W"}
    }]

    inserted = upsert_products(sample)
    assert inserted == 1

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT offer_id, title_pl, price_pln, source_platform, source_url FROM products WHERE offer_id = 'test_powerbank_001'")
            row = cur.fetchone()
            assert row is not None
            assert row[0] == "test_powerbank_001"
            assert row[1] == "Powerbank 20000mAh Szybkie Ładowanie 22.5W"
            assert float(row[2]) == 34.66
            # Manager fields exist
            assert row[3] == "1688"
            assert "detail.1688.com" in row[4]

