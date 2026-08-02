import React, { useState } from 'react';
import { Search, Camera, Link as LinkIcon, TrendingDown, Sparkles, Tag, ArrowUpRight } from 'lucide-react';

interface HomeScreenProps {
  onSearchSubmit: (query: string) => void;
  onSelectProduct: (productId: string) => void;
}

export const HomeScreen: React.FC<HomeScreenProps> = ({ onSearchSubmit, onSelectProduct }) => {
  const [searchInput, setSearchInput] = useState('');

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchInput.trim()) {
      onSearchSubmit(searchInput.trim());
    }
  };

  const dealItems = [
    {
      id: 'mst_9f83a210',
      title: 'Sony WH-1000XM5 Black (Giao Nha Trang)',
      category: 'Наушники',
      minPrice: 7490000,
      oldPrice: 8900000,
      dropPercent: 16,
      platforms: ['shopee', 'lazada'],
      image: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&q=80'
    },
    {
      id: 'mst_macbook_m3',
      title: 'Apple MacBook Air 15" M3 (8/256)',
      category: 'Ноутбуки',
      minPrice: 28990000,
      oldPrice: 34000000,
      dropPercent: 15,
      platforms: ['shopee', 'shein'],
      image: 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400&q=80'
    },
    {
      id: 'mst_dyson_airwrap',
      title: 'Dyson Airwrap Long Complete (VN Plug)',
      category: 'Красота и здоровье',
      minPrice: 11900000,
      oldPrice: 14500000,
      dropPercent: 18,
      platforms: ['lazada', 'shopee', 'shein'],
      image: 'https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=400&q=80'
    }
  ];

  return (
    <div className="space-y-6 pb-24 pt-2">
      {/* Header Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-orange-600 via-rose-600 to-cyan-600 p-5 text-white shadow-xl glow-cyan">
        <div className="relative z-10 space-y-2">
          <div className="inline-flex items-center gap-1.5 rounded-full bg-white/20 px-3 py-1 text-xs font-semibold backdrop-blur-md">
            <Sparkles className="w-3.5 h-3.5" /> SmartSearch Nha Trang 🇻🇳
          </div>
          <h1 className="text-2xl font-extrabold tracking-tight">Сравнение цен во Вьетнаме</h1>
          <p className="text-xs text-orange-100 opacity-90">
            Ищем лучшую цену по Shopee VN, Lazada VN и Shein с доставкой в Нячанг.
          </p>
        </div>
        <div className="absolute -bottom-6 -right-6 w-32 h-32 bg-white/10 rounded-full blur-xl pointer-events-none" />
      </div>

      {/* Quick Actions Search Bar */}
      <form onSubmit={handleSearch} className="space-y-3">
        <div className="relative">
          <input
            type="text"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Введите название, артикул или вставьте ссылку..."
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
            onClick={() => onSearchSubmit('Наушники по фото')}
            className="flex items-center justify-center gap-2 rounded-xl bg-slate-900/80 border border-slate-800/80 p-3 text-xs font-medium text-slate-300 hover:border-cyan-500/50 hover:text-cyan-400 transition-all"
          >
            <Camera className="w-4 h-4 text-cyan-400" /> Поиск по фото
          </button>
          <button
            type="button"
            onClick={() => onSearchSubmit('https://www.wildberries.ru/catalog/12345')}
            className="flex items-center justify-center gap-2 rounded-xl bg-slate-900/80 border border-slate-800/80 p-3 text-xs font-medium text-slate-300 hover:border-cyan-500/50 hover:text-cyan-400 transition-all"
          >
            <LinkIcon className="w-4 h-4 text-cyan-400" /> Поиск по ссылке
          </button>
        </div>
      </form>

      {/* Top Deals Section */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="flex items-center gap-2 text-base font-bold text-slate-100">
            <TrendingDown className="w-5 h-5 text-emerald-400" />
            Аномальные скидки дня
          </h2>
          <span className="text-xs text-cyan-400 font-medium cursor-pointer">Все 24 🔥</span>
        </div>

        <div className="grid gap-3">
          {dealItems.map((item) => (
            <div
              key={item.id}
              onClick={() => onSelectProduct(item.id)}
              className="glass-panel group relative flex items-center gap-3.5 rounded-xl p-3 border border-slate-800 hover:border-cyan-500/40 transition-all cursor-pointer"
            >
              <img
                src={item.image}
                alt={item.title}
                className="w-20 h-20 rounded-lg object-cover bg-slate-800 group-hover:scale-105 transition-transform"
              />
              <div className="flex-1 min-w-0 space-y-1">
                <div className="flex items-center gap-2">
                  <span className="inline-flex items-center gap-1 rounded bg-emerald-500/10 px-1.5 py-0.5 text-[10px] font-bold text-emerald-400 border border-emerald-500/20">
                    <Tag className="w-3 h-3" /> -{item.dropPercent}%
                  </span>
                  <span className="text-[10px] text-slate-400 uppercase tracking-wider">{item.category}</span>
                </div>
                <h3 className="text-xs font-semibold text-slate-100 truncate">{item.title}</h3>
                <div className="flex items-baseline gap-2">
                  <span className="text-sm font-extrabold text-emerald-400">{item.minPrice.toLocaleString()} ₫</span>
                  <span className="text-xs text-slate-500 line-through">{item.oldPrice.toLocaleString()} ₫</span>
                </div>
              </div>
              <ArrowUpRight className="w-5 h-5 text-slate-600 group-hover:text-cyan-400 transition-colors" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
