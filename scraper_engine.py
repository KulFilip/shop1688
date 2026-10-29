import os
import sys
import time
import asyncio
from typing import List, Optional
from models import build_search_url, OfferSummary, OfferDetail
from parser import parse_search_results_html, parse_offer_detail_html

CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
]

def find_system_browser() -> Optional[str]:
    for path in CHROME_PATHS:
        if os.path.exists(path):
            return path
    return None

class Scraper1688:
    def __init__(self, headless: bool = True, user_data_dir: Optional[str] = None):
        self.headless = headless
        self.user_data_dir = user_data_dir or os.path.abspath(os.path.join(os.path.dirname(__file__), "browser_profile"))
        self.executable_path = find_system_browser()

    async def search_phrase(self, keyword: str, max_pages: int = 1) -> List[OfferSummary]:
        """
        Launches browser with stealth flags and searches 1688 for the given phrase.
        Returns list of parsed OfferSummary objects.
        """
        from playwright.async_api import async_playwright

        all_offers: List[OfferSummary] = []
        async with async_playwright() as p:
            launch_args = [
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-infobars",
                "--lang=zh-CN,zh,en-US,en"
            ]

            browser_context = await p.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                executable_path=self.executable_path,
                headless=self.headless,
                args=launch_args,
                viewport={"width": 1440, "height": 900},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )

            page = await browser_context.new_page()

            # Evade navigator.webdriver detection
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)

            for page_num in range(1, max_pages + 1):
                url = build_search_url(keyword, page=page_num)
                print(f"[1688 Scraper] Otwieranie strony wyszukiwania ({page_num}/{max_pages}): {url}")
                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    # Scroll down to trigger lazy loading of search cards
                    await page.evaluate("window.scrollBy(0, 1000);")
                    await asyncio.sleep(2)
                    await page.evaluate("window.scrollBy(0, 1500);")
                    await asyncio.sleep(2)

                    content = await page.content()
                    offers = parse_search_results_html(content)
                    print(f"[1688 Scraper] Znaleziono {len(offers)} ofert na stronie {page_num}.")
                    all_offers.extend(offers)
                except Exception as e:
                    print(f"[1688 Scraper] Błąd podczas ładowania strony {page_num}: {e}")

            await browser_context.close()
        return all_offers

    async def get_offer_details(self, offer_url_or_id: str) -> Optional[OfferDetail]:
        """
        Fetches full offer page, scrolls through description to trigger lazy-loaded images,
        and parses attributes, full gallery and tiered pricing.
        """
        from playwright.async_api import async_playwright

        if "1688.com/offer/" in offer_url_or_id:
            import re
            m = re.search(r'/offer/(\d+)\.html', offer_url_or_id)
            offer_id = m.group(1) if m else "unknown"
            url = offer_url_or_id
        else:
            offer_id = str(offer_url_or_id)
            url = f"https://detail.1688.com/offer/{offer_id}.html"

        async with async_playwright() as p:
            browser_context = await p.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                executable_path=self.executable_path,
                headless=self.headless,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
                viewport={"width": 1440, "height": 900}
            )

            page = await browser_context.new_page()
            await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
            
            print(f"[1688 Scraper] Pobieranie szczegółów oferty ID: {offer_id} ({url})...")
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=35000)
                # Scroll gradually to load all product description images
                for step in range(4):
                    await page.evaluate(f"window.scrollBy(0, 800);")
                    await asyncio.sleep(1)

                content = await page.content()
                detail = parse_offer_detail_html(offer_id, content)
                await browser_context.close()
                return detail
            except Exception as e:
                print(f"[1688 Scraper] Błąd pobierania oferty {offer_id}: {e}")
                await browser_context.close()
                return None
