import pytest
from seeder import generate_powerbank_catalog

def test_generate_powerbank_catalog_50_items():
    items = generate_powerbank_catalog(count=50, margin=0.30)
    assert len(items) == 50

    first = items[0]
    assert first["category"] == "power bank"
    assert first["margin"] == 0.30
    assert first["price_pln"] is not None and first["price_pln"] > 0
    assert first["price_uah"] is not None and first["price_uah"] > 0
    assert first["weight"] != ""
    assert first["dimensions"] != ""
    assert first["main_image"].startswith("http")
    assert first["source_platform"] == "1688"
    assert "1688.com" in first["source_url"]
    assert first["source_seller"] != ""

    # Ensure all offer_ids are unique
    ids = [x["offer_id"] for x in items]
    assert len(set(ids)) == 50

