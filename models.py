import re
import urllib.parse
from typing import List, Optional
from pydantic import BaseModel, Field

class OfferSummary(BaseModel):
    offer_id: str
    title: str
    price: Optional[float] = None
    currency: str = "CNY"
    min_order_quantity: Optional[int] = None
    sales_count: Optional[str] = None
    seller_name: Optional[str] = None
    seller_location: Optional[str] = None
    detail_url: str
    main_image_url: Optional[str] = None

class OfferDetail(BaseModel):
    offer_id: str
    title: str
    price: Optional[float] = None
    prices_tiered: List[dict] = Field(default_factory=list) # e.g. [{"range": ">=2", "price": 15.5}]
    main_images: List[str] = Field(default_factory=list)
    description_images: List[str] = Field(default_factory=list)
    attributes: dict = Field(default_factory=dict)
    seller_name: Optional[str] = None
    raw_description_text: Optional[str] = None

def build_search_url(keyword: str, page: int = 1) -> str:
    """Builds clean 1688 search URL for a given keyword."""
    encoded_kw = urllib.parse.quote(keyword)
    return f"https://s.1688.com/youyuan/index.htm?tab=all&keywords={encoded_kw}&beginPage={page}"

def sanitize_filename(name: str) -> str:
    """Sanitizes strings for safe Windows/cross-platform filesystem paths."""
    clean = re.sub(r'[\\/*?:"<>|]', "_", name)
    clean = re.sub(r'\s+', "_", clean)
    clean = re.sub(r'_+', "_", clean).strip("_")
    return clean[:80] if clean else "unnamed"

def normalize_image_url(url: str, high_res: bool = True) -> str:
    """
    Normalizes 1688/Alibaba CDN image URLs, removes thumbnail downscales (e.g. .search.jpg, 220x220)
    and ensures proper https:// protocol.
    """
    if not url:
        return ""
    if url.startswith("//"):
        url = "https:" + url
    elif not url.startswith("http"):
        url = "https://" + url

    if high_res:
        # Strip downscale dimensions (e.g. _300x300.jpg -> .jpg, _220x220.png -> .png)
        url = re.sub(r'_\d+x\d+(\.[a-zA-Z0-9]+)$', r'\1', url)
        # Strip .search suffix before extension
        url = re.sub(r'\.search(\.[a-zA-Z0-9]+)$', r'\1', url, flags=re.IGNORECASE)
        # Strip webp conversion suffix if any
        url = re.sub(r'_\.webp$', '', url, flags=re.IGNORECASE)
    return url
