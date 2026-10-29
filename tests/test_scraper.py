import os
import sys
import pytest
from models import build_search_url, sanitize_filename, normalize_image_url, OfferSummary, OfferDetail
from parser import parse_search_results_html, parse_offer_detail_html
from storage import save_offers_to_csv, save_and_download_offer_package

def test_build_search_url():
    url = build_search_url("led strip", page=2)
    assert "keywords=led%20strip" in url
    assert "beginPage=2" in url
    assert url.startswith("https://s.1688.com/")

def test_sanitize_filename():
    raw = 'Smart Watch: Waterproof / 4G (Test & Demo)*?'
    clean = sanitize_filename(raw)
    assert ":" not in clean
    assert "/" not in clean
    assert "?" not in clean
    assert clean == "Smart_Watch_Waterproof_4G_(Test_&_Demo)"

def test_normalize_image_url():
    # Downscaled thumbnail URL from 1688 CDN
    downscaled = "//cbu01.alicdn.com/img/ibank/2020/123/456/789_300x300.jpg"
    high_res = normalize_image_url(downscaled, high_res=True)
    assert high_res == "https://cbu01.alicdn.com/img/ibank/2020/123/456/789.jpg"

    # Search thumbnail with .search.jpg
    search_thumb = "https://cbu01.alicdn.com/img/ibank/2021/item.search.jpg"
    assert normalize_image_url(search_thumb) == "https://cbu01.alicdn.com/img/ibank/2021/item.jpg"

def test_parse_search_results_html_embedded_json():
    # Simulates modern 1688 search page with embedded window.__INITIAL_DATA__
    html = """
    <html>
      <head></head>
      <body>
        <script>
          window.__INITIAL_DATA__ = {
            "data": {
              "offerList": [
                {
                  "id": "6789123456",
                  "title": "<em>Xiaomi</em> Mini Latarka LED USB C",
                  "price": "14.50",
                  "saleQuantity": "2000+",
                  "companyName": "Shenzhen Technology Co.",
                  "imageUrl": "//cbu01.alicdn.com/img/ibank/flashlight_220x220.jpg"
                },
                {
                  "offerId": "7890123456",
                  "subject": "Kabel USB-C Szybkie Ładowanie 66W",
                  "formatPrice": "2.80",
                  "sales": "50000+",
                  "companyName": "Dongguan Cable Factory",
                  "imageUrl": "https://cbu01.alicdn.com/img/ibank/cable.jpg"
                }
              ]
            }
          };
        </script>
      </body>
    </html>
    """
    offers = parse_search_results_html(html)
    assert len(offers) == 2
    assert offers[0].offer_id == "6789123456"
    assert offers[0].title == "Xiaomi Mini Latarka LED USB C"
    assert offers[0].price == 14.5
    assert offers[0].sales_count == "2000+"
    assert offers[0].main_image_url == "https://cbu01.alicdn.com/img/ibank/flashlight.jpg"

    assert offers[1].offer_id == "7890123456"
    assert offers[1].title == "Kabel USB-C Szybkie Ładowanie 66W"
    assert offers[1].price == 2.80

def test_parse_search_results_html_dom_fallback():
    # Simulates fallback DOM structure
    html = """
    <div class="sm-offer-item" data-offer-id="99887766">
      <a class="title" href="//detail.1688.com/offer/99887766.html">Etui na telefon silikonowe przezroczyste</a>
      <span class="price">¥ 1.99</span>
      <img src="//cbu01.alicdn.com/img/case_100x100.png" />
    </div>
    """
    offers = parse_search_results_html(html)
    assert len(offers) == 1
    assert offers[0].offer_id == "99887766"
    assert offers[0].title == "Etui na telefon silikonowe przezroczyste"
    assert offers[0].price == 1.99
    assert offers[0].main_image_url == "https://cbu01.alicdn.com/img/case.png"
    assert offers[0].detail_url == "https://detail.1688.com/offer/99887766.html"

def test_parse_offer_detail_html():
    html = """
    <div class="od-pc-offer-title">
      <h1 class="title-text">Bezprzewodowe Słuchawki Bluetooth TWS Pro</h1>
    </div>
    <div class="detail-gallery-turn">
      <img src="//cbu01.alicdn.com/tws_photo1_400x400.jpg" />
      <img src="//cbu01.alicdn.com/tws_photo2_400x400.jpg" />
    </div>
    <div class="ladder-price-item">
      <span class="range">≥ 2 szt.</span>
      <span class="price">25.00</span>
    </div>
    <div class="ladder-price-item">
      <span class="range">≥ 100 szt.</span>
      <span class="price">19.50</span>
    </div>
    <div class="offer-attr-item">
      <span>Bluetooth</span>: <span>5.3</span>
    </div>
    <div class="offer-attr-item">
      <span>Bateria</span>: <span>400mAh</span>
    </div>
    <div id="desc-lazyload-container">
      <p>Bardzo wysoka jakość dźwięku, redukcja szumów ENC.</p>
      <img src="//cbu01.alicdn.com/desc_chart_800x800.jpg" />
    </div>
    """
    detail = parse_offer_detail_html("123456789", html)
    assert detail.offer_id == "123456789"
    assert "Słuchawki Bluetooth" in detail.title
    assert len(detail.main_images) == 2
    assert detail.main_images[0] == "https://cbu01.alicdn.com/tws_photo1.jpg"
    assert len(detail.description_images) == 1
    assert detail.description_images[0] == "https://cbu01.alicdn.com/desc_chart.jpg"
    assert len(detail.prices_tiered) == 2
    assert detail.prices_tiered[0]["price"] == "25.00"
    assert detail.attributes.get("Bluetooth") == "5.3"
    assert "redukcja szumów ENC" in detail.raw_description_text

def test_storage_csv_and_package(tmp_path):
    # Test CSV export
    csv_file = tmp_path / "test_offers.csv"
    sample_offers = [
        OfferSummary(
            offer_id="111",
            title="Test Item 1",
            price=10.0,
            detail_url="https://detail.1688.com/offer/111.html",
            main_image_url="https://cbu01.alicdn.com/img1.jpg"
        )
    ]
    save_offers_to_csv(sample_offers, str(csv_file))
    assert csv_file.exists()
    content = csv_file.read_text(encoding="utf-8-sig")
    assert "Test Item 1" in content
    assert "111" in content

    # Test folder & detail packaging
    detail = OfferDetail(
        offer_id="222",
        title="Pakiet Testowy Produktu",
        attributes={"Materiał": "Stal nierdzewna"},
        prices_tiered=[{"range": ">=10", "price": "12.00"}],
        raw_description_text="Długi opis parametrów..."
    )
    result = save_and_download_offer_package(detail, str(tmp_path))
    folder = result["folder"]
    assert os.path.exists(folder)
    assert os.path.exists(os.path.join(folder, "details.json"))
    assert os.path.exists(os.path.join(folder, "opis_produktu.txt"))
    with open(os.path.join(folder, "opis_produktu.txt"), "r", encoding="utf-8") as f:
        txt = f.read()
        assert "Stal nierdzewna" in txt
        assert "12.00 CNY" in txt
