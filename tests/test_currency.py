import pytest
from currency import get_nbp_exchange_rates, calculate_prices

def test_calculate_prices():
    # 100 CNY, margin = 0.30 (30%), cny_pln = 0.5925, uah_pln = 0.0867
    rates = {"CNY_PLN": 0.5925, "UAH_PLN": 0.0867}
    res = calculate_prices(price_cny=100.0, margin=0.30, rates=rates)
    
    # Base cost in PLN = 100 * 0.5925 = 59.25 PLN
    # Price with margin = 59.25 * 1.30 = 77.025 PLN (rounded 77.03 PLN)
    assert res["price_pln"] == 77.03
    # Price in UAH = 77.03 / 0.0867 = 888.466 -> 888.47 UAH
    assert res["price_uah"] == 888.47
    assert res["original_price_cny"] == 100.0
    assert res["margin"] == 0.30

def test_calculate_prices_zero_or_none():
    rates = {"CNY_PLN": 0.5925, "UAH_PLN": 0.0867}
    res = calculate_prices(price_cny=None, margin=0.30, rates=rates)
    assert res["price_pln"] is None
    assert res["price_uah"] is None
