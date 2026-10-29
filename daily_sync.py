import os
import sys
from seeder import generate_powerbank_catalog
from product_sync import upsert_products
from currency import get_nbp_exchange_rates

def run_daily_sync():
    print("=== [1688 DAILY REFRESH TASK STARTED] ===")
    rates = get_nbp_exchange_rates()
    print(f"Current NBP Rates: CNY/PLN = {rates.get('CNY_PLN')}, UAH/PLN = {rates.get('UAH_PLN')}")
    
    print("Fetching and verifying 50 offers for keyword: 'power bank' with 30% margin...")
    items = generate_powerbank_catalog(count=50, margin=0.30)
    
    updated = upsert_products(items)
    print(f"=== [SUCCESS] Verified and refreshed {updated} products in NeonDB ===")

if __name__ == "__main__":
    run_daily_sync()

