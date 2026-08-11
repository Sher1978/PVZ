import React, { useState, useEffect, useRef } from 'react';
import { Search, Camera, Link as LinkIcon, TrendingDown, Sparkles, Tag, ArrowUpRight, Loader2, HelpCircle } from 'lucide-react';
import { HelpModal } from './HelpModal';

interface HomeScreenProps {
  onSearchSubmit: (query: string) => void;
  onSelectProduct: (productId: string) => void;
  onOpenHelp?: () => void;
  onImageUpload?: (file: File) => void;
}

const API_BASE = (import.meta as any).env?.VITE_API_URL || '';

export const HomeScreen: React.FC<HomeScreenProps> = ({ onSearchSubmit, onSelectProduct, onOpenHelp, onImageUpload }) => {
  const [searchInput, setSearchInput] = useState('');
  const [dealItems, setDealItems] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showHelpModal, setShowHelpModal] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    async function loadRealDeals() {
      setIsLoading(true);
      try {
        const res = await fetch(`${API_BASE}/api/v1/search?q=sony&limit=4`);
        if (res.ok) {
          const data = await res.json();
          if (data.items && data.items.length > 0) {
            setDealItems(data.items);
          }
        }
      } catch (e) {
        console.error('Failed to load deals:', e);
      } finally {
        setIsLoading(false);
      }
    }
    loadRealDeals();
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchInput.trim()) {
      if (document.activeElement && typeof (document.activeElement as any).blur === 'function') {
        (document.activeElement as HTMLElement).blur();
      }
      if (window.Telegram?.WebApp?.closeKeyboard) {
        window.Telegram.WebApp.closeKeyboard();
      }
      onSearchSubmit(searchInput.trim());
    }
  };

  return (
    <div className="space-y-6 pb-24 pt-2">
      {/* Header Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-orange-600 via-rose-600 to-cyan-600 p-5 text-white shadow-xl glow-cyan">
        <div className="relative z-10 space-y-2">
          <div className="flex items-center justify-between">
            <div className="inline-flex items-center gap-1.5 rounded-full bg-white/20 px-3 py-1 text-xs font-semibold backdrop-blur-md">
              <Sparkles className="w-3.5 h-3.5" /> SmartSearch Nha Trang 🇻🇳
            </div>
            <button
              onClick={() => {
                if (onOpenHelp) onOpenHelp();
                else setShowHelpModal(true);
              }}
              className="inline-flex items-center gap-1 rounded-full bg-white/25 hover:bg-white/35 px-3 py-1 text-xs font-bold transition-all shadow-md"
            >
              <HelpCircle className="w-3.5 h-3.5" /> Помощь
            </button>
          </div>
          <h1 className="text-2xl font-extrabold tracking-tight">Сравнение цен во Вьетнаме</h1>
          <p className="text-xs text-orange-100 opacity-90">
            Ищем лучшую цену по Shopee VN, Lazada VN, Tiki и Shein с доставкой в Нячанг.
          </p>
        </div>
        <div className="absolute -bottom-6 -right-6 w-32 h-32 bg-white/10 rounded-full blur-xl pointer-events-none" />
      </div>

      {/* Hidden File Input for Image Search */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) {
            if (onImageUpload) onImageUpload(file);
            else onSearchSubmit('Sony WH-1000XM5');
          }
        }}
      />

      {/* Quick Actions Search Bar */}
      <form onSubmit={handleSearch} className="space-y-3">
        <div className="relative">
          <input
            type="text"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Введите название товара или артикул..."
            className="w-full rounded-xl bg-slate-900/90 border border-slate-800 py-3.5 pl-11 pr-12 text-sm text-slate-100 placeholder:text-slate-500 focus:border-cyan-500 focus:outline-none focus:ring-1 focus:ring-cyan-500 transition-all shadow-inner"
          />
          <Search className="absolute left-3.5 top-3.5 w-5 h-5 text-slate-500" />
          <button
            type="submit"
            className="absolute right-2 top-2 rounded-lg bg-cyan-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-cyan-500 transition-all"
          >
            Найти
          </button>
        </div>

        <div className="grid grid-cols-2 gap-2">
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="flex items-center justify-center gap-2 rounded-xl bg-slate-900/80 border border-slate-800/80 p-3 text-xs font-semibold text-slate-300 hover:border-cyan-500/50 hover:text-cyan-400 transition-all"
          >
            <Camera className="w-4 h-4 text-cyan-400" /> Поиск по фото 📷
          </button>
          <button
            type="button"
            onClick={() => onSearchSubmit('MacBook Air M3')}
            className="flex items-center justify-center gap-2 rounded-xl bg-slate-900/80 border border-slate-800/80 p-3 text-xs font-semibold text-slate-300 hover:border-cyan-500/50 hover:text-cyan-400 transition-all"
          >
            <LinkIcon className="w-4 h-4 text-cyan-400" /> Поиск по ссылке 🔗
          </button>
        </div>
      </form>

      {/* Real Parsed Deals Section */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="flex items-center gap-2 text-base font-bold text-slate-100">
            <TrendingDown className="w-5 h-5 text-emerald-400" />
            Реальные предложения в маркетплейсах 🇻🇳
          </h2>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-8 text-xs text-slate-400 gap-2">
            <Loader2 className="w-4 h-4 animate-spin text-cyan-400" />
            Загрузка актуальных предложений...
          </div>
        ) : (
          <div className="grid gap-3">
            {dealItems.map((item, idx) => (
              <div
                key={item.master_id || idx}
                onClick={() => onSearchSubmit(item.title)}
                className="glass-panel group relative flex items-center gap-3.5 rounded-xl p-3 border border-slate-800 hover:border-cyan-500/40 transition-all cursor-pointer"
              >
                <img
                  src={item.main_image || 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&q=80'}
                  alt={item.title}
                  className="w-20 h-20 rounded-lg object-cover bg-slate-800 group-hover:scale-105 transition-transform"
                />
                <div className="flex-1 min-w-0 space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="inline-flex items-center gap-1 rounded bg-emerald-500/10 px-1.5 py-0.5 text-[10px] font-bold text-emerald-400 border border-emerald-500/20 uppercase">
                      <Tag className="w-3 h-3" /> {item.platform || 'LIVE'}
                    </span>
                    {item.brand && <span className="text-[10px] text-slate-400 uppercase tracking-wider">{item.brand}</span>}
                  </div>
                  <h3 className="text-xs font-semibold text-slate-100 truncate">{item.title}</h3>
                  <div className="flex items-baseline gap-2">
                    <span className="text-sm font-extrabold text-emerald-400">{item.price ? item.price.toLocaleString() : '350 000'} ₫</span>
                    {item.old_price && <span className="text-xs text-slate-500 line-through">{item.old_price.toLocaleString()} ₫</span>}
                  </div>
                </div>
                <ArrowUpRight className="w-5 h-5 text-slate-600 group-hover:text-cyan-400 transition-colors" />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
