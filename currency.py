import urllib.request
import json
from typing import Optional, Dict

def get_nbp_exchange_rates() -> Dict[str, float]:
    """
    Fetches mid exchange rates for CNY and UAH against PLN from official NBP Web API Table A.
    Returns dictionary with keys: CNY_PLN, UAH_PLN.
    Falls back to safe default rates if API is unavailable.
    """
    rates = {"CNY_PLN": 0.5925, "UAH_PLN": 0.0867}
    try:
        req = urllib.request.Request(
            "http://api.nbp.pl/api/exchangerates/rates/a/cny/?format=json",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            rates["CNY_PLN"] = float(data["rates"][0]["mid"])
    except Exception as e:
        print(f"Warning: Failed to fetch CNY rate from NBP: {e}")

    try:
        req = urllib.request.Request(
            "http://api.nbp.pl/api/exchangerates/rates/a/uah/?format=json",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            rates["UAH_PLN"] = float(data["rates"][0]["mid"])
    except Exception as e:
        print(f"Warning: Failed to fetch UAH rate from NBP: {e}")

    return rates

def calculate_prices(price_cny: Optional[float], margin: float = 0.30, rates: Optional[Dict[str, float]] = None) -> Dict[str, Optional[float]]:
    """
    Calculates PLN and UAH retail prices with target margin.
    price_pln = price_cny * CNY_PLN * (1 + margin)
    price_uah = price_pln / UAH_PLN
    """
    if price_cny is None or price_cny <= 0:
        return {
            "original_price_cny": price_cny,
            "margin": margin,
            "price_pln": None,
            "price_uah": None
        }

    if not rates:
        rates = get_nbp_exchange_rates()

    cny_pln = rates.get("CNY_PLN", 0.5925)
    uah_pln = rates.get("UAH_PLN", 0.0867)

    base_pln = price_cny * cny_pln
    retail_pln = round(base_pln * (1.0 + margin), 2)
    retail_uah = round(retail_pln / uah_pln, 2) if uah_pln > 0 else None

    return {
        "original_price_cny": round(price_cny, 2),
        "margin": margin,
        "price_pln": retail_pln,
        "price_uah": retail_uah
    }

