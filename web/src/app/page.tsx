'use client';

import React, { useState, useEffect, useMemo } from 'react';
import { translations } from '@/lib/types';
import { 
  Zap, 
  ShieldCheck, 
  Truck, 
  ExternalLink, 
  SlidersHorizontal, 
  Search, 
  Lock, 
  Unlock,
  CheckCircle2,
  BatteryCharging
} from 'lucide-react';

interface ProductItem {
  id: number;
  offer_id: string;
  category: string;
  title: string;
  description: string;
  weight: string;
  dimensions: string;
  main_image: string;
  images: string[];
  price_pln: number;
  price_uah: number;
  in_stock: boolean;
  price_cny?: number;
  margin?: number;
  source_platform?: string;
  source_url?: string;
  source_seller?: string;
  raw_attributes?: Record<string, any>;
  updated_at?: string;
}

export default function ShopPage() {
  const [lang, setLang] = useState<'pl' | 'ua'>('pl');
  const [currency, setCurrency] = useState<'PLN' | 'UAH'>('PLN');
  const [isManager, setIsManager] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [products, setProducts] = useState<ProductItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedProduct, setSelectedProduct] = useState<ProductItem | null>(null);

  const t = translations[lang];

  useEffect(() => {
    async function fetchProducts() {
      setLoading(true);
      try {
        const params = new URLSearchParams();
        params.set('lang', lang);
        if (isManager) params.set('manager', 'true');
        params.set('category', 'power bank');
        params.set('limit', '50');

        const res = await fetch(`/api/products?${params.toString()}`);
        const data = await res.json();
        if (data.success) {
          setProducts(data.products);
        }
      } catch (err) {
        console.error('Fetch products error:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchProducts();
  }, [lang, isManager]);

  const filteredProducts = useMemo(() => {
    if (!searchQuery.trim()) return products;
    const q = searchQuery.toLowerCase();
    return products.filter(
      (p) =>
        p.title.toLowerCase().includes(q) ||
        p.description.toLowerCase().includes(q) ||
        p.weight.toLowerCase().includes(q)
    );
  }, [products, searchQuery]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 antialiased selection:bg-cyan-500 selection:text-white">
      {/* Top Status Notification */}
      <div className="border-b border-slate-800 bg-slate-900/60 backdrop-blur px-4 py-2 text-xs flex justify-between items-center text-slate-400">
        <div className="flex items-center gap-2">
          <span className="inline-block w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span>{t.dailyRefreshNotice}</span>
        </div>
        <div className="flex items-center gap-4">
          <button
            onClick={() => setIsManager(!isManager)}
            className={`flex items-center gap-1.5 px-2 py-1 rounded text-xs font-mono transition-all ${
              isManager
                ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            {isManager ? <Unlock className="w-3.5 h-3.5" /> : <Lock className="w-3.5 h-3.5" />}
            {isManager ? t.managerActive : t.managerMode}
          </button>
        </div>
      </div>

      {/* Main Header */}
      <header className="sticky top-0 z-40 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 to-blue-500 flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <div>
              <span className="font-extrabold text-xl tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
                NORDICVOLT
              </span>
              <span className="block text-xs font-medium text-cyan-400">MINIMAL TECH STUDIO</span>
            </div>
          </div>

          {/* Search bar */}
          <div className="flex-1 max-w-md hidden md:block">
            <div className="relative">
              <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder={t.searchPlaceholder}
                className="w-full bg-slate-900 border border-slate-800 rounded-full pl-10 pr-4 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
              />
            </div>
          </div>

          {/* Lang & Currency Switchers */}
          <div className="flex items-center gap-3">
            {/* Currency Selector */}
            <div className="inline-flex rounded-lg bg-slate-900 p-1 border border-slate-800 text-xs font-semibold">
              <button
                onClick={() => setCurrency('PLN')}
                className={`px-3 py-1.5 rounded-md transition-all ${
                  currency === 'PLN'
                    ? 'bg-cyan-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                PLN (zł)
              </button>
              <button
                onClick={() => setCurrency('UAH')}
                className={`px-3 py-1.5 rounded-md transition-all ${
                  currency === 'UAH'
                    ? 'bg-cyan-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                UAH (грн)
              </button>
            </div>

            {/* Language Selector */}
            <div className="inline-flex rounded-lg bg-slate-900 p-1 border border-slate-800 text-xs font-semibold">
              <button
                onClick={() => setLang('pl')}
                className={`px-2.5 py-1.5 rounded-md transition-all ${
                  lang === 'pl' ? 'bg-slate-700 text-white' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                PL
              </button>
              <button
                onClick={() => setLang('ua')}
                className={`px-2.5 py-1.5 rounded-md transition-all ${
                  lang === 'ua' ? 'bg-slate-700 text-white' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                UA
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Banner */}
      <section className="relative overflow-hidden border-b border-slate-800 py-12 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-slate-900/50 to-transparent">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-950/60 border border-cyan-800/40 text-cyan-300 text-xs font-medium mb-3">
              <BatteryCharging className="w-3.5 h-3.5" />
              <span>{t.powerBanks} • 50 Ofert Deterministycznych</span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
              {t.powerBanks}
            </h1>
            <p className="mt-2 text-slate-400 text-sm sm:text-base leading-relaxed">
              {t.tagline}
            </p>
          </div>

          <div className="grid grid-cols-2 gap-4 text-xs font-medium text-slate-300">
            <div className="flex items-center gap-2 p-3 rounded-xl bg-slate-900/80 border border-slate-800">
              <Truck className="w-4 h-4 text-cyan-400 flex-shrink-0" />
              <span>{t.deliveryFast}</span>
            </div>
            <div className="flex items-center gap-2 p-3 rounded-xl bg-slate-900/80 border border-slate-800">
              <ShieldCheck className="w-4 h-4 text-emerald-400 flex-shrink-0" />
              <span>{t.qualityGuarantee}</span>
            </div>
          </div>
        </div>
      </section>

      {/* Catalog Grid */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="flex justify-between items-center mb-6">
          <span className="text-sm font-medium text-slate-400">
            {t.productsFound}: <strong className="text-white font-mono">{filteredProducts.length}</strong>
          </span>
          <div className="flex items-center gap-2 text-xs text-slate-500">
            <SlidersHorizontal className="w-3.5 h-3.5" />
            <span>Katalog z marżą 30% • NBP Live</span>
          </div>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {Array.from({ length: 8 }).map((_, idx) => (
              <div key={idx} className="h-80 rounded-2xl bg-slate-900/60 animate-pulse border border-slate-800"></div>
            ))}
          </div>
        ) : filteredProducts.length === 0 ? (
          <div className="text-center py-20 text-slate-500">{t.noProducts}</div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {filteredProducts.map((p) => {
              const displayPrice = currency === 'PLN' ? `${p.price_pln.toFixed(2)} zł` : `${p.price_uah.toFixed(2)} ₴`;

              return (
                <div
                  key={p.offer_id}
                  className="group relative flex flex-col rounded-2xl bg-slate-900/60 border border-slate-800 hover:border-cyan-500/50 hover:shadow-xl hover:shadow-cyan-950/20 transition-all duration-300 overflow-hidden"
                >
                  {/* Image container */}
                  <div className="relative aspect-square w-full overflow-hidden bg-slate-950">
                    <img
                      src={p.main_image}
                      alt={p.title}
                      className="h-full w-full object-cover object-center group-hover:scale-105 transition-transform duration-500"
                    />
                    <div className="absolute top-3 left-3">
                      <span className="inline-flex items-center gap-1 rounded-full bg-slate-900/90 backdrop-blur px-2.5 py-1 text-[11px] font-medium text-emerald-400 border border-emerald-500/20">
                        <CheckCircle2 className="w-3 h-3" />
                        {t.inStock}
                      </span>
                    </div>

                    {/* Manager Badge if active */}
                    {isManager && p.source_platform && (
                      <div className="absolute bottom-2 left-2 right-2 rounded-lg bg-amber-950/90 border border-amber-500/40 p-2 text-[10px] text-amber-200 backdrop-blur">
                        <div className="font-semibold text-amber-400 flex justify-between">
                          <span>1688 ID: {p.offer_id}</span>
                          <span>CNY: ¥{p.price_cny} (+{((p.margin || 0.3) * 100).toFixed(0)}%)</span>
                        </div>
                        <div className="truncate text-slate-300 mt-0.5">{p.source_seller}</div>
                        <a
                          href={p.source_url}
                          target="_blank"
                          rel="noreferrer"
                          className="mt-1 inline-flex items-center gap-1 text-amber-300 underline font-medium hover:text-white"
                        >
                          <ExternalLink className="w-3 h-3" />
                          {t.viewSupplier}
                        </a>
                      </div>
                    )}
                  </div>

                  {/* Body */}
                  <div className="p-4 flex-1 flex flex-col justify-between">
                    <div>
                      <h3 className="font-semibold text-sm line-clamp-2 text-slate-100 group-hover:text-cyan-300 transition-colors">
                        {p.title}
                      </h3>
                      <p className="mt-1 text-xs text-slate-400 line-clamp-2">
                        {p.description}
                      </p>

                      {/* Specs pills */}
                      <div className="mt-3 flex flex-wrap gap-2 text-[11px] font-mono text-slate-400">
                        {p.weight && (
                          <span className="px-2 py-0.5 rounded bg-slate-800/80 border border-slate-700/50">
                            {t.weight}: {p.weight}
                          </span>
                        )}
                        {p.dimensions && (
                          <span className="px-2 py-0.5 rounded bg-slate-800/80 border border-slate-700/50">
                            {t.dimensions}: {p.dimensions}
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between">
                      <div>
                        <span className="text-[10px] uppercase tracking-wider text-slate-500 font-bold block">
                          {t.price}
                        </span>
                        <span className="text-lg font-black text-white tracking-tight">
                          {displayPrice}
                        </span>
                      </div>
                      <button
                        onClick={() => setSelectedProduct(p)}
                        className="rounded-xl bg-cyan-600 hover:bg-cyan-500 px-3.5 py-2 text-xs font-semibold text-white shadow-md shadow-cyan-900/40 transition-colors"
                      >
                        {t.addToCart}
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </main>

      {/* Product Detail Modal */}
      {selectedProduct && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-lg w-full p-6 text-slate-100 shadow-2xl relative">
            <button
              onClick={() => setSelectedProduct(null)}
              className="absolute top-4 right-4 text-slate-400 hover:text-white text-lg font-mono"
            >
              ✕
            </button>
            <div className="aspect-video w-full rounded-2xl overflow-hidden mb-4 bg-slate-950">
              <img
                src={selectedProduct.main_image}
                alt={selectedProduct.title}
                className="w-full h-full object-cover"
              />
            </div>
            <h2 className="text-xl font-bold">{selectedProduct.title}</h2>
            <p className="mt-2 text-sm text-slate-300 leading-relaxed">
              {selectedProduct.description}
            </p>
            <div className="mt-4 space-y-1 text-xs text-slate-400 font-mono">
              <div>• {t.weight}: <strong className="text-slate-200">{selectedProduct.weight}</strong></div>
              <div>• {t.dimensions}: <strong className="text-slate-200">{selectedProduct.dimensions}</strong></div>
            </div>
            <div className="mt-6 flex items-center justify-between">
              <span className="text-2xl font-black text-cyan-400">
                {currency === 'PLN' ? `${selectedProduct.price_pln.toFixed(2)} zł` : `${selectedProduct.price_uah.toFixed(2)} ₴`}
              </span>
              <button
                onClick={() => {
                  alert(lang === 'pl' ? 'Produkt dodany do koszyka testowego!' : 'Товар додано до тестового кошика!');
                  setSelectedProduct(null);
                }}
                className="bg-cyan-600 hover:bg-cyan-500 text-white px-5 py-2.5 rounded-xl font-semibold text-sm transition-all shadow-lg shadow-cyan-950/50"
              >
                {t.addToCart}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Minimal Footer */}
      <footer className="border-t border-slate-800/80 py-8 text-center text-xs text-slate-500 bg-slate-950">
        <p>© 2026 NordicVolt Electronics. Wszelkie prawa zastrzeżone.</p>
        <p className="mt-1">Dostawa realizowana na terenie Polski oraz Ukrainy.</p>
      </footer>
    </div>
  );
}
