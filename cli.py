import os
import sys
import argparse
import asyncio
from typing import List

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from models import OfferSummary
from scraper_engine import Scraper1688
from storage import save_offers_to_csv, save_and_download_offer_package

async def main_async():
    parser = argparse.ArgumentParser(description="1688.com Product & Image Scraper by Search Phrase or URL")
    parser.add_argument("--query", "-q", type=str, help="Fraza wyszukiwania (np. 'led strip' lub 'smart watch')")
    parser.add_argument("--url", "-u", type=str, help="Bezpośredni URL oferty 1688 do pobrania ze zdjęciami")
    parser.add_argument("--pages", "-p", type=int, default=1, help="Liczba stron wyników do przeszukania (domyślnie: 1)")
    parser.add_argument("--download-top", "-d", type=int, default=0, help="Liczba pierwszych ofert, dla których pobrać pełną paczkę zdjęć i opis (np. 3)")
    parser.add_argument("--output-dir", "-o", type=str, default="./output", help="Katalog wyjściowy na pliki i zdjęcia")
    parser.add_argument("--headful", action="store_true", help="Uruchom przeglądarkę w trybie widocznym (przydatne do rozwiązania ewentualnej captchy)")

    args = parser.parse_args()

    if not args.query and not args.url:
        print("BŁĄD: Musisz podać --query (frazę szukaną) lub --url (bezpośredni link do oferty).")
        parser.print_help()
        sys.exit(1)

    scraper = Scraper1688(headless=not args.headful)
    out_dir = os.path.abspath(args.output_dir)
    os.makedirs(out_dir, exist_ok=True)

    # Tryb 1: Bezpośredni link do jednej oferty
    if args.url:
        print(f"\n[1688] Pobieranie bezpośredniej oferty: {args.url}")
        detail = await scraper.get_offer_details(args.url)
        if detail:
            print(f" -> Tytuł: {detail.title}")
            print(f" -> Zdjęcia główne: {len(detail.main_images)}")
            print(f" -> Zdjęcia w opisie: {len(detail.description_images)}")
            print(f" -> Zapisywanie paczki do katalogu {out_dir}...")
            res = save_and_download_offer_package(detail, out_dir)
            print(f" ✓ Zapisano do: {res['folder']}")
            print(f" ✓ Pobranych zdjęć głównych: {res['main_images_count']}")
            print(f" ✓ Pobranych zdjęć opisu: {res['desc_images_count']}")
        else:
            print(" ✗ Nie udało się pobrać szczegółów oferty.")
        return

    # Tryb 2: Wyszukiwanie po frazie
    if args.query:
        print(f"\n[1688] Szukanie ofert dla frazy: '{args.query}' (Stron: {args.pages})...")
        offers: List[OfferSummary] = await scraper.search_phrase(args.query, max_pages=args.pages)
        print(f" ✓ Znaleziono łącznie {len(offers)} ofert.")

        if not offers:
            print(" ! Brak wyników lub wymagana interakcja na stronie 1688. Uruchom z flagą --headful, aby zweryfikować.")
            return

        csv_path = os.path.join(out_dir, f"oferty_{args.query}.csv")
        save_offers_to_csv(offers, csv_path)
        print(f" ✓ Zapisano zestawienie {len(offers)} ofert do CSV: {csv_path}")

        # Jeśli zażądano pobrania pełnych paczek i zdjęć dla pierwszych N ofert
        if args.download_top > 0:
            count = min(args.download_top, len(offers))
            print(f"\n[1688] Rozpoczynanie pobierania pełnych opisów i zdjęć dla TOP {count} ofert...")
            for idx, off in enumerate(offers[:count], 1):
                print(f"\n[{idx}/{count}] Pobieranie oferty ID {off.offer_id}: {off.title[:45]}...")
                detail = await scraper.get_offer_details(off.detail_url)
                if detail:
                    res = save_and_download_offer_package(detail, os.path.join(out_dir, "pobrane_produkty"))
                    print(f" -> Zapisano zdjęcia i opis: {res['folder']}")
                else:
                    print(f" -> Pominięto ofertę {off.offer_id} (błąd pobierania).")

        print("\n=== ZAKOŃCZONO POMYŚLNIE ===")

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
