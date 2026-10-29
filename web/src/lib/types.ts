export interface CustomerProduct {
  id: number;
  offer_id: string;
  category: string;
  title: string;
  description: string;
  weight: string;
  dimensions: string;
  main_image: string;
  images: string[];
  price: number;
  currency: 'PLN' | 'UAH';
  in_stock: boolean;
}

export interface ManagerProduct extends CustomerProduct {
  price_cny: number;
  margin: number;
  source_platform: string;
  source_url: string;
  source_seller: string;
  raw_attributes: Record<string, unknown>;
  updated_at: string;
}

export const translations = {
  pl: {
    siteTitle: 'NordicVolt | Minimalistyczna Elektronika & Akcesoria',
    tagline: 'Zaawansowane banki energii i akcesoria ładowania najwyższej klasy.',
    powerBanks: 'Banki Energii (Power Bank)',
    searchPlaceholder: 'Szukaj produktów (np. 20000mAh, MagSafe, 65W)...',
    allCategories: 'Wszystkie produkty',
    inStock: 'W magazynie',
    outOfStock: 'Tymczasowo niedostępny',
    weight: 'Waga',
    dimensions: 'Wymiary',
    price: 'Cena',
    addToCart: 'Dodaj do koszyka',
    specs: 'Specyfikacja techniczna',
    currencyToggle: 'Zmień walutę',
    langToggle: 'Język / Мова',
    managerMode: 'Panel Managera (Poufne źródła 1688)',
    managerActive: 'Tryb Inspekcji Managera Włączony',
    sourcePlatform: 'Platforma źródłowa',
    sourceSeller: 'Dostawca hurtowy',
    originalCny: 'Cena bazowa CNY',
    appliedMargin: 'Naliczona marża',
    viewSupplier: 'Przejdź do oferty dostawcy',
    dailyRefreshNotice: 'Katalog synchronizowany codziennie o 04:00 CET z weryfikacją stanów.',
    productsFound: 'Znaleziono ofert',
    noProducts: 'Brak produktów spełniających wybrane kryteria.',
    deliveryFast: 'Wysyłka w 24h z magazynu UE',
    qualityGuarantee: 'Gwarancja jakości 24 miesiące'
  },
  ua: {
    siteTitle: 'NordicVolt | Мінімалістична Електроніка та Аксесуари',
    tagline: 'Сучасні повербанки та аксесуари живлення преміальної якості.',
    powerBanks: 'Повербанки (Power Bank)',
    searchPlaceholder: 'Пошук товарів (наприклад, 20000mAh, MagSafe, 65W)...',
    allCategories: 'Всі товари',
    inStock: 'В наявності',
    outOfStock: 'Тимчасово немає',
    weight: 'Вага',
    dimensions: 'Розміри',
    price: 'Ціна',
    addToCart: 'Додати в кошик',
    specs: 'Технічні характеристики',
    currencyToggle: 'Змінити валюту',
    langToggle: 'Język / Мова',
    managerMode: 'Панель Менеджера (Конфіденційні джерела 1688)',
    managerActive: 'Режим Перевірки Менеджера Увімкнено',
    sourcePlatform: 'Платформа-постачальник',
    sourceSeller: 'Оптовий постачальник',
    originalCny: 'Базова ціна CNY',
    appliedMargin: 'Встановлена маржа',
    viewSupplier: 'Відкрити картку постачальника',
    dailyRefreshNotice: 'Каталог оновлюється щодня о 04:00 CET з перевіркою наявності.',
    productsFound: 'Знайдено пропозицій',
    noProducts: 'Товарів за вашим запитом не знайдено.',
    deliveryFast: 'Доставка 24-48 годин зі складу ЄС',
    qualityGuarantee: 'Гарантія якості 24 місяці'
  }
};

