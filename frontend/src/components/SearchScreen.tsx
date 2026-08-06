import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Search, Filter, ExternalLink, Star, ArrowUpDown, Loader2, Zap, X } from 'lucide-react';

interface SearchScreenProps {
  initialQuery?: string;
  onSelectProduct: (product: any) => void;
}

const API_BASE = (import.meta as any).env?.VITE_API_URL || '';

const PLATFORM_CONFIG: Record<string, { label: string; color: string; badge?: string }> = {
  shopee: { label: 'Shopee VN 🇻🇳',  color: 'bg-orange-500', badge: 'ACCESSTRADE' },
  lazada: { label: 'Lazada VN 🇻🇳',  color: 'bg-blue-600',   badge: 'ACCESSTRADE' },
  tiki:   { label: 'Tiki VN 🇻🇳',    color: 'bg-sky-500' },
  shein:  { label: 'Shein Global',    color: 'bg-emerald-600' },
  kiki:   { label: 'Kiki Fashion 👗', color: 'bg-pink-500',   badge: 'ACCESSTRADE' },
};

interface ApiItem {
  master_id: string;
  title: string;
  brand?: string;
  main_image?: string;
  images?: string[];
  price: number;
  old_price?: number;
  platform: string;
  currency: string;
  url: string;
  rating?: number;
  reviews_count?: number;
}


export const SearchScreen: React.FC<SearchScreenProps> = ({ initialQuery = 'Sony WH-1000XM5', onSelectProduct }) => {
  const [query, setQuery] = useState(initialQuery);
  const [selectedPlatform, setSelectedPlatform] = useState('all');
  const [sortMode, setSortMode] = useState<'relevance' | 'price_asc' | 'price_desc'>('relevance');
  const [results, setResults] = useState<ApiItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (initialQuery && initialQuery !== query) {
      setQuery(initialQuery);
    }
  }, [initialQuery]);

  const dismissKeyboard = () => {
    if (inputRef.current) {
      inputRef.current.blur();
    }
    if (document.activeElement && typeof (document.activeElement as any).blur === 'function') {
      (document.activeElement as HTMLElement).blur();
    }
    if (window.Telegram?.WebApp?.closeKeyboard) {
      window.Telegram.WebApp.closeKeyboard();
    }
  };

  const handleClearSearch = () => {
    setQuery('');
    setResults([]);
    setHasSearched(false);
  };

  const doSearch = useCallback(async (q: string, platform: string, sort: string) => {
    if (!q.trim()) return;
    setIsLoading(true);
    setHasSearched(true);
    try {
      const params = new URLSearchParams({ q, marketplace: platform, sort, limit: '15' });
      const res = await fetch(`${API_BASE}/api/v1/search?${params}`);
      if (res.ok) {
        const data = await res.json();
        setResults(data.items || []);
      }
    } catch (e) {
      console.error('Search error:', e);
    } finally {
      setIsLoading(false);
      dismissKeyboard();
    }
  }, []);

  useEffect(() => {
    const debounce = setTimeout(() => doSearch(query, selectedPlatform, sortMode), 600);
    return () => clearTimeout(debounce);
  }, [query, selectedPlatform, sortMode, doSearch]);

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    dismissKeyboard();
    doSearch(query, selectedPlatform, sortMode);
  };

  const handleToggleSort = () => {
    if (sortMode === 'relevance') {
      setSortMode('price_asc');
    } else if (sortMode === 'price_asc') {
      setSortMode('price_desc');
    } else {
      setSortMode('relevance');
    }
  };

  const platforms = [
    { id: 'all',    label: 'Все платформы (VN)' },
    { id: 'shopee', label: 'Shopee VN 🇻🇳' },
    { id: 'lazada', label: 'Lazada VN 🇻🇳' },
    { id: 'tiki',   label: 'Tiki VN 🇻🇳' },
    { id: 'kiki',   label: 'Kiki Fashion 👗' },
    { id: 'shein',  label: 'Shein Global' },
  ];

  // Group API results by master_id for display
  const grouped = results.reduce<Record<string, ApiItem[]>>((acc, item) => {
    const key = item.master_id;
    if (!acc[key]) acc[key] = [];
    acc[key].push(item);
    return acc;
  }, {});

  const masterItems = Object.entries(grouped).map(([id, offers]) => {
    const best = offers.reduce((a, b) => a.price < b.price ? a : b);
    const allImages = Array.from(
      new Set(
        offers.flatMap((o: any) => o.images || (o.main_image ? [o.main_image] : [])).filter(Boolean)
      )
    );
    return {
      id,
      title: best.title,
      brand: best.brand,
      image: best.main_image,
      images: allImages.length > 0 ? allImages : [best.main_image].filter(Boolean),
      offers,
      minPrice: best.price,
      rating: best.rating,
      reviewsCount: best.reviews_count
    };
  });

  if (sortMode === 'price_asc') {
    masterItems.sort((a, b) => a.minPrice - b.minPrice);
  } else if (sortMode === 'price_desc') {
    masterItems.sort((a, b) => b.minPrice - a.minPrice);
  }

  return (
    <div className="space-y-4 pb-24 pt-2">
      {/* Search Header */}
      <form onSubmit={handleFormSubmit} className="relative">
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Поиск товаров по ключевому слову или ссылке..."
          className="w-full rounded-xl bg-slate-900 border border-slate-800 py-3.5 pl-11 pr-10 text-sm text-slate-100 focus:border-cyan-500 focus:outline-none"
        />
        <Search className="absolute left-3.5 top-3.5 w-5 h-5 text-slate-500" />
        {query && (
          <button
            type="button"
            onClick={handleClearSearch}
            className="absolute right-3 top-3.5 p-1 rounded-full text-slate-400 hover:text-white hover:bg-slate-800 transition-all"
            title="Очистить поиск"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </form>

      {/* Platform Filter Tabs */}
      <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-none">
        {platforms.map((p) => (
          <button
            key={p.id}
            onClick={() => setSelectedPlatform(p.id)}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-all ${
              selectedPlatform === p.id
                ? 'bg-cyan-500 text-white font-semibold shadow-md shadow-cyan-500/20'
                : 'bg-slate-900 text-slate-400 border border-slate-800 hover:text-slate-200'
            }`}
          >
            {p.label}
          </button>
        ))}
      </div>

      {/* Sort Info Bar */}
      <div className="flex items-center justify-between text-xs text-slate-400 px-1">
        <span>
          {isLoading ? (
            <span className="flex items-center gap-1.5">
              <Loader2 className="w-3.5 h-3.5 animate-spin text-cyan-400" />
              Поиск на платформах...
            </span>
          ) : hasSearched ? (
            `Найдено ${masterItems.length} карточек`
          ) : (
            'Введите запрос для поиска'
          )}
        </span>
        <button
          onClick={handleToggleSort}
          className="flex items-center gap-1 text-cyan-400 font-medium hover:underline"
        >
          <ArrowUpDown className="w-3.5 h-3.5" />
          {sortMode === 'price_asc' ? 'Сначала дешевле' : sortMode === 'price_desc' ? 'Сначала дороже' : 'По релевантности'}
        </button>
      </div>

      {/* Search Results List */}
      <div className="space-y-3">
        {masterItems.map((item) => (
          <div
            key={item.id}
            onClick={() => onSelectProduct(item)}
            className="glass-panel rounded-2xl p-4 border border-slate-800 hover:border-cyan-500/40 transition-all cursor-pointer space-y-3"
          >
            <div className="flex gap-3">
              <img
                src={item.image || 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&q=80'}
                alt={item.title}
                className="w-24 h-24 rounded-xl object-cover bg-slate-800"
              />
              <div className="flex-1 min-w-0 space-y-1">
                {item.brand && <span className="text-[10px] text-slate-500 uppercase tracking-wider">{item.brand}</span>}
                <h3 className="text-xs font-bold text-slate-100 line-clamp-2">{item.title}</h3>
                {item.rating != null && (
                  <div className="flex items-center gap-1.5 text-xs text-amber-400 font-medium">
                    <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
                    <span>{item.rating.toFixed(1)}</span>
                    {item.reviewsCount != null && <span className="text-slate-500">({item.reviewsCount.toLocaleString()} отзывов)</span>}
                  </div>
                )}
              </div>
            </div>

            {/* Platform Offers Matrix */}
            <div className="pt-2 border-t border-slate-800/80 space-y-1.5">
              <div className="text-[11px] font-semibold text-slate-400">Предложения ({item.offers.length}):</div>
              <div className="grid gap-1.5">
                {item.offers.map((offer, idx) => {
                  const cfg = PLATFORM_CONFIG[offer.platform] || { label: offer.platform, color: 'bg-slate-500' };
                  const isBest = offer.price === item.minPrice;
                  return (
                    <div
                      key={idx}
                      className={`flex items-center justify-between text-xs rounded-lg px-3 py-2 border ${
                        isBest ? 'bg-emerald-500/10 border-emerald-500/30' : 'bg-slate-900/60 border-slate-800/50'
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <span className={`w-2 h-2 rounded-full ${cfg.color}`} />
                        <span className="font-medium text-slate-200">{cfg.label}</span>
                        {cfg.badge && (
                          <span className="flex items-center gap-0.5 rounded bg-violet-500/20 px-1.5 py-0.5 text-[8px] font-bold text-violet-300">
                            <Zap className="w-2 h-2" />{cfg.badge}
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`font-extrabold ${isBest ? 'text-emerald-400' : 'text-slate-100'}`}>
                          {offer.price.toLocaleString()} ₫
                        </span>
                        {isBest && (
                          <span className="rounded bg-emerald-500/20 px-1.5 py-0.5 text-[9px] font-bold text-emerald-300">
                            Лучшая
                          </span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        ))}

        {/* Empty state */}
        {!isLoading && hasSearched && masterItems.length === 0 && (
          <div className="text-center py-12 text-slate-500">
            <Search className="w-10 h-10 mx-auto mb-3 opacity-30" />
            <p className="text-sm">Товары не найдены</p>
            <p className="text-xs mt-1">Попробуйте другой запрос</p>
          </div>
        )}
      </div>
    </div>
  );
};
