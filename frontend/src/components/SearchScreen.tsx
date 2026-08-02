import React, { useState } from 'react';
import { Search, Filter, ExternalLink, Star, ArrowUpDown } from 'lucide-react';

interface SearchScreenProps {
  initialQuery?: string;
  onSelectProduct: (productId: string) => void;
}

export const SearchScreen: React.FC<SearchScreenProps> = ({ initialQuery = 'Sony WH-1000XM5', onSelectProduct }) => {
  const [query, setQuery] = useState(initialQuery);
  const [selectedPlatform, setSelectedPlatform] = useState('all');
  const [sortMode, setSortMode] = useState<'relevance' | 'price_asc' | 'price_desc'>('relevance');

  const platforms = [
    { id: 'all', label: 'Все платфомы (VN)' },
    { id: 'shopee', label: 'Shopee VN 🇻🇳' },
    { id: 'lazada', label: 'Lazada VN 🇻🇳' },
    { id: 'shein', label: 'Shein VN' },
    { id: 'wb', label: 'Wildberries' },
    { id: 'ozon', label: 'Ozon' },
  ];

  const searchResults = [
    {
      id: 'mst_9f83a210',
      title: 'Sony WH-1000XM5 Black (Chính Hãng - Giao Nha Trang)',
      category: 'Электроника / Наушники',
      minPrice: 7490000,
      maxPrice: 8900000,
      offersCount: 3,
      image: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&q=80',
      rating: 4.9,
      reviewsCount: 420,
      offers: [
        { name: 'Shopee VN', price: 7490000, oldPrice: 8900000, color: 'bg-orange-500', currency: '₫' },
        { name: 'Lazada VN', price: 7650000, oldPrice: 8500000, color: 'bg-blue-600', currency: '₫' },
        { name: 'Shein Global', price: 7890000, oldPrice: 8200000, color: 'bg-emerald-600', currency: '₫' },
      ]
    },
    {
      id: 'mst_airpods_max',
      title: 'Apple AirPods Max Space Gray (Bảo hành 12 tháng tại VN)',
      category: 'Электроника / Наушники',
      minPrice: 13990000,
      maxPrice: 15500000,
      offersCount: 2,
      image: 'https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=400&q=80',
      rating: 4.8,
      reviewsCount: 280,
      offers: [
        { name: 'Shopee Mall', price: 13990000, oldPrice: 15500000, color: 'bg-orange-500', currency: '₫' },
        { name: 'Lazada LazMall', price: 14200000, oldPrice: 15200000, color: 'bg-blue-600', currency: '₫' },
      ]
    }
  ];

  return (
    <div className="space-y-4 pb-24 pt-2">
      {/* Search Header */}
      <div className="relative">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Поиск товаров на всех площадках..."
          className="w-full rounded-xl bg-slate-900 border border-slate-800 py-3.5 pl-11 pr-4 text-sm text-slate-100 focus:border-cyan-500 focus:outline-none"
        />
        <Search className="absolute left-3.5 top-3.5 w-5 h-5 text-slate-500" />
      </div>

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

      {/* Sort Options */}
      <div className="flex items-center justify-between text-xs text-slate-400 px-1">
        <span>Найдено 2 сопоставленных Master-карточки</span>
        <button
          onClick={() => setSortMode(sortMode === 'price_asc' ? 'price_desc' : 'price_asc')}
          className="flex items-center gap-1 text-cyan-400 font-medium hover:underline"
        >
          <ArrowUpDown className="w-3.5 h-3.5" />
          {sortMode === 'price_asc' ? 'Сначала дешевле' : sortMode === 'price_desc' ? 'Сначала дороже' : 'По релевантности'}
        </button>
      </div>

      {/* Search Results List */}
      <div className="space-y-3">
        {searchResults.map((item) => (
          <div
            key={item.id}
            onClick={() => onSelectProduct(item.id)}
            className="glass-panel rounded-2xl p-4 border border-slate-800 hover:border-cyan-500/40 transition-all cursor-pointer space-y-3"
          >
            <div className="flex gap-3">
              <img
                src={item.image}
                alt={item.title}
                className="w-24 h-24 rounded-xl object-cover bg-slate-800"
              />
              <div className="flex-1 min-w-0 space-y-1">
                <span className="text-[10px] text-slate-500 uppercase tracking-wider">{item.category}</span>
                <h3 className="text-xs font-bold text-slate-100 line-clamp-2">{item.title}</h3>

                <div className="flex items-center gap-1.5 text-xs text-amber-400 font-medium">
                  <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
                  <span>{item.rating}</span>
                  <span className="text-slate-500">({item.reviewsCount} отзывов)</span>
                </div>
              </div>
            </div>

            {/* Platform Offers Matrix */}
            <div className="pt-2 border-t border-slate-800/80 space-y-1.5">
              <div className="text-[11px] font-semibold text-slate-400">Сравнение {item.offersCount} предложений:</div>
              <div className="grid gap-1.5">
                {item.offers.map((offer, idx) => (
                  <div key={idx} className="flex items-center justify-between text-xs bg-slate-900/60 rounded-lg px-3 py-2 border border-slate-800/50">
                    <div className="flex items-center gap-2">
                      <span className={`w-2 h-2 rounded-full ${offer.color}`} />
                      <span className="font-medium text-slate-200">{offer.name}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="font-extrabold text-emerald-400">{offer.price.toLocaleString()} ₫</span>
                      {idx === 0 && (
                        <span className="rounded bg-emerald-500/20 px-1.5 py-0.5 text-[9px] font-bold text-emerald-300">
                          Лучшая цена
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
