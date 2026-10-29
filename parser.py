import json
import re
from typing import List, Optional
from bs4 import BeautifulSoup
from models import OfferSummary, OfferDetail, normalize_image_url

def parse_search_results_html(html_content: str) -> List[OfferSummary]:
    """
    Parses 1688 search page HTML or embedded script JSON data to extract OfferSummary list.
    Handles both modern window.__INITIAL_DATA__ JSON state and traditional DOM elements.
    """
    offers: List[OfferSummary] = []
    
    # 1. Try extracting from embedded state JSON (window.__INITIAL_DATA__ or data-state)
    json_match = re.search(r'window\.__INITIAL_DATA__\s*=\s*(\{.*?\});', html_content, re.DOTALL)
    if not json_match:
        json_match = re.search(r'data:\s*(\{.*?"offerList".*?\})\s*</script>', html_content, re.DOTALL)

    if json_match:
        try:
            data = json.loads(json_match.group(1))
            offer_items = []
            if "data" in data and "offerList" in data["data"]:
                offer_items = data["data"]["offerList"]
            elif "offerList" in data:
                offer_items = data["offerList"]
                
            for item in offer_items:
                offer_id = str(item.get("id") or item.get("offerId") or "")
                title = item.get("title") or item.get("subject") or "Bez tytułu"
                # Strip HTML tags from title if any
                title = re.sub(r'<[^>]+>', '', title).strip()
                price_val = None
                try:
                    price_val = float(item.get("price") or item.get("formatPrice") or 0.0)
                except (ValueError, TypeError):
                    pass
                
                img = normalize_image_url(item.get("imageUrl") or item.get("imgUrl") or "")
                url = item.get("detailUrl") or f"https://detail.1688.com/offer/{offer_id}.html"
                if url.startswith("//"):
                    url = "https:" + url

                if offer_id:
                    offers.append(OfferSummary(
                        offer_id=offer_id,
                        title=title,
                        price=price_val,
                        sales_count=str(item.get("saleQuantity") or item.get("sales") or ""),
                        seller_name=item.get("companyName") or item.get("loginId"),
                        seller_location=item.get("province") or item.get("city"),
                        detail_url=url,
                        main_image_url=img
                    ))
        except Exception:
            pass

    # 2. Fallback to DOM parsing via BeautifulSoup
    if not offers:
        soup = BeautifulSoup(html_content, "html.parser")
        card_selectors = [
            ".sm-offer-item",
            ".space-common-card",
            "[data-offer-id]",
            ".offer-card"
        ]
        
        cards = []
        for selector in card_selectors:
            found = soup.select(selector)
            if found:
                cards = found
                break

        for card in cards:
            offer_id = card.get("data-offer-id") or ""
            link_el = card.select_one("a.title, a[href*='detail.1688.com/offer']")
            if not offer_id and link_el and link_el.get("href"):
                id_match = re.search(r'/offer/(\d+)\.html', link_el["href"])
                if id_match:
                    offer_id = id_match.group(1)

            if not offer_id:
                continue

            title = ""
            if link_el:
                title = link_el.get_text(strip=True)
            if not title:
                title_el = card.select_one(".title, .subject")
                if title_el:
                    title = title_el.get_text(strip=True)

            detail_url = link_el["href"] if link_el and link_el.get("href") else f"https://detail.1688.com/offer/{offer_id}.html"
            if detail_url.startswith("//"):
                detail_url = "https:" + detail_url

            price = None
            price_el = card.select_one(".price, .money, .sm-offer-priceNum")
            if price_el:
                price_match = re.search(r'[\d.]+', price_el.get_text(strip=True))
                if price_match:
                    try:
                        price = float(price_match.group(0))
                    except ValueError:
                        pass

            img_el = card.select_one("img")
            img_url = ""
            if img_el:
                raw_src = img_el.get("src") or img_el.get("data-src") or img_el.get("data-lazyload-src") or ""
                img_url = normalize_image_url(raw_src)

            offers.append(OfferSummary(
                offer_id=offer_id,
                title=title or f"Oferta {offer_id}",
                price=price,
                detail_url=detail_url,
                main_image_url=img_url
            ))

    return offers

def parse_offer_detail_html(offer_id: str, html_content: str) -> OfferDetail:
    """Parses 1688 product detail page HTML to extract full attributes and all high-res photos."""
    soup = BeautifulSoup(html_content, "html.parser")
    
    # 1. Title
    title = ""
    title_el = soup.select_one("h1.title-text, .d-title, .od-pc-offer-title, h1")
    if title_el:
        title = title_el.get_text(strip=True)
    if not title:
        title = f"1688 Oferta {offer_id}"

    # 2. Main gallery images
    main_images = []
    # Try scripts or thumbnail list
    img_candidates = soup.select(".tab-content-container img, .detail-gallery-turn img, .box-img img, ul.nav-tabs li img")
    for img in img_candidates:
        src = img.get("src") or img.get("data-src") or img.get("data-lazyload-src") or ""
        norm = normalize_image_url(src)
        if norm and norm not in main_images:
            main_images.append(norm)

    # 3. Description images (often in #desc-lazyload-container or .content-detail)
    desc_images = []
    desc_container = soup.select_one("#desc-lazyload-container, .content-detail, #content-detail")
    if desc_container:
        for img in desc_container.select("img"):
            src = img.get("src") or img.get("data-src") or img.get("data-lazyload-src") or ""
            norm = normalize_image_url(src)
            if norm and norm not in desc_images:
                desc_images.append(norm)

    # 4. Attributes / Spec table
    attributes = {}
    attr_items = soup.select(".obj-sku, .offer-attr-item, .obj-leading tr, .offer-attr .de-item")
    for item in attr_items:
        text = item.get_text(strip=True)
        if ":" in text:
            parts = [p.strip() for p in text.split(":", 1)]
            if len(parts) == 2 and parts[0] and parts[1]:
                attributes[parts[0]] = parts[1]
        elif "：" in text: # Full-width Chinese colon
            parts = [p.strip() for p in text.split("：", 1)]
            if len(parts) == 2 and parts[0] and parts[1]:
                attributes[parts[0]] = parts[1]

    # 5. Prices tiered
    prices_tiered = []
    price_blocks = soup.select(".price-item, .ladder-price-item")
    for pb in price_blocks:
        amount_el = pb.select_one(".price, .value")
        range_el = pb.select_one(".unit, .amount, .range")
        if amount_el:
            prices_tiered.append({
                "range": range_el.get_text(strip=True) if range_el else "",
                "price": amount_el.get_text(strip=True)
            })

    # Raw description text
    raw_desc = desc_container.get_text("\n", strip=True) if desc_container else ""

    return OfferDetail(
        offer_id=str(offer_id),
        title=title,
        main_images=main_images,
        description_images=desc_images,
        attributes=attributes,
        prices_tiered=prices_tiered,
        raw_description_text=raw_desc
    )
