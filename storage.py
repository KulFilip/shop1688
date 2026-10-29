import os
import re
import csv
import json
import requests
from typing import List, Optional
from models import OfferSummary, OfferDetail, sanitize_filename

def download_image(url: str, save_path: str, timeout: int = 15) -> bool:
    """Downloads an image from CDN and saves to disk."""
    if not url:
        return False
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Referer": "https://www.1688.com/"
        }
        res = requests.get(url, headers=headers, timeout=timeout, stream=True)
        if res.status_code == 200:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, "wb") as f:
                for chunk in res.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
    except Exception:
        pass
    return False

def save_offers_to_csv(offers: List[OfferSummary], output_csv_path: str):
    """Saves search offer summaries to CSV."""
    os.makedirs(os.path.dirname(os.path.abspath(output_csv_path)), exist_ok=True)
    fieldnames = list(OfferSummary.model_fields.keys())
    
    with open(output_csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for o in offers:
            writer.writerow(o.model_dump())

def save_offer_detail_to_json(detail: OfferDetail, output_json_path: str):
    """Saves complete offer details to formatted JSON."""
    os.makedirs(os.path.dirname(os.path.abspath(output_json_path)), exist_ok=True)
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(detail.model_dump(), f, ensure_ascii=False, indent=2)

def save_and_download_offer_package(detail: OfferDetail, base_dir: str) -> dict:
    """
    Creates an organized directory for the offer, downloads main and description images,
    and saves full specification and description text.
    """
    safe_title = sanitize_filename(detail.title)
    folder_name = f"{detail.offer_id}_{safe_title[:30]}"
    target_dir = os.path.join(base_dir, folder_name)
    images_dir = os.path.join(target_dir, "images")
    desc_dir = os.path.join(target_dir, "description_images")

    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(desc_dir, exist_ok=True)

    # 1. Download gallery images
    downloaded_main = []
    for idx, img_url in enumerate(detail.main_images, 1):
        ext = "jpg"
        if ".png" in img_url.lower():
            ext = "png"
        elif ".webp" in img_url.lower():
            ext = "webp"
        img_path = os.path.join(images_dir, f"main_{idx}.{ext}")
        if download_image(img_url, img_path):
            downloaded_main.append(img_path)

    # 2. Download description images
    downloaded_desc = []
    for idx, img_url in enumerate(detail.description_images, 1):
        ext = "jpg"
        if ".png" in img_url.lower():
            ext = "png"
        elif ".webp" in img_url.lower():
            ext = "webp"
        img_path = os.path.join(desc_dir, f"desc_{idx}.{ext}")
        if download_image(img_url, img_path):
            downloaded_desc.append(img_path)

    # 3. Save details JSON & Readme
    json_path = os.path.join(target_dir, "details.json")
    save_offer_detail_to_json(detail, json_path)

    txt_path = os.path.join(target_dir, "opis_produktu.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"TYTUŁ: {detail.title}\n")
        f.write(f"ID OFERTY: {detail.offer_id}\n\n")
        f.write("SPECYFIKACJA / ATRYBUTY:\n")
        for k, v in detail.attributes.items():
            f.write(f" - {k}: {v}\n")
        f.write("\nCENY HURTOWE (PROGOWE):\n")
        for p in detail.prices_tiered:
            f.write(f" - Ilość: {p.get('range')} => Cena: {p.get('price')} CNY\n")
        f.write("\nTEKST Z OPISU:\n")
        f.write(detail.raw_description_text or "Brak dodatkowego tekstu.")

    return {
        "folder": target_dir,
        "main_images_count": len(downloaded_main),
        "desc_images_count": len(downloaded_desc)
    }
