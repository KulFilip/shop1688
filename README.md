# 1688.com Product, Image & Description Scraper

Narzędzie w Pythonie umożliwiające wyszukiwanie ofert hurtowych na **1688.com** po dowolnej frazie (np. `led strip`, `smart watch`), pobieranie specyfikacji, cen progowych oraz pobieranie wszystkich zdjęć (zarówno galerii głównej w wysokiej rozdzielczości, jak i grafik ze środka opisu technicznego).

---

## 🚀 Możliwości
- **Szukanie po frazie**: generuje listę znalezionych ofert hurtowych z cenami i linkami do pliku `.csv`.
- **Ekstrakcja galerii i opisów**: pobiera zdjęcia główne (automatycznie usuwa pomniejszenia CDN takie jak `_300x300.jpg`, zwracając oryginały).
- **Pobieranie zdjęć z opisu**: wykonuje automatyczny scroll lazy-loadingu w dół i pobiera ryciny specyfikacji technicznej.
- **Tabela specyfikacji**: zapisuje atrybuty oferty do `opis_produktu.txt` oraz pełnej struktury `details.json`.
- **Omijanie anty-bota**: używa silnika Chromium z flagami wyłączającymi detekcję `navigator.webdriver` i trwałym profilem przeglądarki (`browser_profile`).

---

## 🛠️ Wymagania i instalacja

Wymagany Python 3.10+ oraz zainstalowane biblioteki:
```bash
pip install playwright beautifulsoup4 pydantic requests pytest
```

---

## 📖 Przykłady użycia

### 1. Wyszukanie ofert po frazie i zapis do CSV:
```bash
python cli.py --query "led strip" --pages 1 --output-dir ./wyniki
```
Zapisze plik `wyniki/oferty_led strip.csv` ze wszystkimi znalezionymi produktami.

### 2. Wyszukanie po frazie + automatyczne pobranie zdjęć i opisów dla TOP 3 produktów:
```bash
python cli.py --query "smart watch" --pages 1 --download-top 3 --output-dir ./wyniki
```
Dla każdego z 3 pierwszych produktów stworzy dedykowany folder zawierający:
- `images/` - zdjęcia z galerii w jakości oryginalnej,
- `description_images/` - zdjęcia i infografiki z opisu oferty,
- `opis_produktu.txt` - specyfikacja, parametry, ceny progowe,
- `details.json` - ustrukturyzowany zrzut danych.

### 3. Pobranie konkretnej oferty ze zdjęciami po linku:
```bash
python cli.py --url "https://detail.1688.com/offer/6789123456.html" --output-dir ./wyniki
```

### 4. Tryb z widocznym oknem przeglądarki (`--headful`):
Gdyby 1688 wymagało przesunięcia suwaka weryfikacji (slider captcha) lub pierwszego logowania:
```bash
python cli.py --query "powerbank" --headful
```
Profil sesji i ciasteczka zostaną zachowane w katalogu `browser_profile/` na przyszłość.

---

## 🧪 Testy jednostkowe (TDD)
Wszystkie testy poprawności modeli, dekodowania parametrów, filtracji zdjęć wysokiej rozdzielczości oraz parsera HTML/JSON uruchamia się poleceniem:
```bash
python -m pytest tests/test_scraper.py -v
```
