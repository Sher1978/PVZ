import React, { useState } from 'react';
import { ArrowLeft, Bell, Heart, ExternalLink, ShieldCheck, TrendingDown, Star, Zap, Package, MapPin, Copy, ShoppingBag, ChevronLeft, ChevronRight } from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip } from 'recharts';
import { PvzModal } from './PvzModal';

export interface ProductOffer {
  platform: string;
  price: number;
  old_price?: number;
  url: string;
  delivery_info?: string;
}

export interface ProductDetailItem {
  id: string;
  title: string;
  brand?: string;
  image?: string;
  images?: string[];
  offers?: ProductOffer[];
}

interface ProductDetailScreenProps {
  productId: string;
  productItem?: ProductDetailItem | null;
  onBack: () => void;
}

const PLATFORM_CONFIG: Record<string, { label: string; color: string; badge?: string; btnBg: string; hoverBg: string }> = {
  shopee: { label: 'Shopee Vietnam Mall 🇻🇳', color: 'bg-orange-500', badge: 'ACCESSTRADE', btnBg: 'bg-orange-600', hoverBg: 'hover:bg-orange-500' },
  lazada: { label: 'Lazada LazMall VN 🇻🇳', color: 'bg-blue-600', badge: 'ACCESSTRADE', btnBg: 'bg-blue-600', hoverBg: 'hover:bg-blue-500' },
  tiki:   { label: 'TikiNOW Express 🇻🇳', color: 'bg-sky-500', btnBg: 'bg-sky-600', hoverBg: 'hover:bg-sky-500' },
  shein:  { label: 'Shein Global', color: 'bg-emerald-600', btnBg: 'bg-emerald-600', hoverBg: 'hover:bg-emerald-500' },
  kiki:   { label: 'Kiki Fashion 👗', color: 'bg-pink-500', badge: 'ACCESSTRADE', btnBg: 'bg-pink-600', hoverBg: 'hover:bg-pink-500' },
};

export const ProductDetailScreen: React.FC<ProductDetailScreenProps> = ({ productId, productItem, onBack }) => {
  const [selectedPeriod, setSelectedPeriod] = useState('3m');
  const [showAlertModal, setShowAlertModal] = useState(false);
  const [showPvzModal, setShowPvzModal] = useState(false);
  const [targetPrice, setTargetPrice] = useState('7000000');
  const [isAlertCreated, setIsAlertCreated] = useState(false);
  const [activeImageIndex, setActiveImageIndex] = useState(0);

  const title = productItem?.title || 'Беспроводные полноразмерные наушники Sony WH-1000XM5 Black';
  const brand = productItem?.brand || 'Sony • Электроника';

  const imagesList = Array.from(
    new Set(
      (productItem?.images && productItem.images.length > 0
        ? productItem.images
        : [productItem?.image]
      ).filter(Boolean) as string[]
    )
  );

  const fallbackImages = [
    'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&q=80',
    'https://images.unsplash.com/photo-1583394838336-acd977736f90?w=600&q=80',
    'https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=600&q=80',
  ];

  const galleryImages = imagesList.length > 0 ? imagesList : fallbackImages;
  const currentImage = galleryImages[activeImageIndex] || galleryImages[0];

  const getMarketplaceLink = (platform: string, customUrl?: string) => {
    if (customUrl && !['https://shopee.vn', 'https://lazada.vn', 'https://tiki.vn', 'https://www.kikifashion.com'].includes(customUrl)) {
      return customUrl;
    }
    const q = encodeURIComponent(title);
    switch (platform) {
      case 'shopee':
        return `https://shopee.vn/search?keyword=${q}`;
      case 'lazada':
        return `https://www.lazada.vn/catalog/?q=${q}`;
      case 'tiki':
        return `https://tiki.vn/search?q=${q}`;
      case 'shein':
        return `https://www.shein.com/pdsearch/${q}`;
      case 'kiki':
        return `https://www.google.com/search?q=${q}+kiki+fashion+vietnam`;
      default:
        return `https://shopee.vn/search?keyword=${q}`;
    }
  };

  const handleCreateAlert = () => {
    if (window.Telegram?.WebApp?.HapticFeedback) {
      window.Telegram.WebApp.HapticFeedback.notificationOccurred('success');
    }
    setIsAlertCreated(true);
    setShowAlertModal(false);
  };

  // Determine actual offers for this item (ONLY show found platform offers)
  const rawOffers: ProductOffer[] = productItem?.offers && productItem.offers.length > 0
    ? productItem.offers
    : [
        {
          platform: 'shopee',
          price: 7490000,
          old_price: 8900000,
          url: getMarketplaceLink('shopee'),
          delivery_info: 'Доставка во Вьетнам: 1-2 дня'
        }
      ];

  const sortedOffers = [...rawOffers].sort((a, b) => a.price - b.price);
  const minPrice = sortedOffers[0]?.price;

  return (
    <div className="space-y-5 pb-28 pt-2">
      {/* Header Bar */}
      <div className="flex items-center justify-between">
        <button
          onClick={onBack}
          className="flex items-center gap-1 rounded-xl bg-slate-900 px-3 py-2 text-xs font-semibold text-slate-300 border border-slate-800 hover:text-white"
        >
          <ArrowLeft className="w-4 h-4" /> Назад
        </button>
        <div className="flex gap-2">
          <button className="p-2 rounded-xl bg-slate-900 text-slate-300 border border-slate-800 hover:text-rose-400">
            <Heart className="w-4 h-4" />
          </button>
          <button
            onClick={() => setShowAlertModal(true)}
            className={`p-2 rounded-xl border transition-all ${
              isAlertCreated
                ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40'
                : 'bg-slate-900 text-slate-300 border-slate-800 hover:text-amber-400'
            }`}
          >
            <Bell className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Main Image Banner with Multi-Image Gallery Carousel */}
      <div className="glass-panel relative rounded-2xl p-4 border border-slate-800 text-center space-y-3">
        <div className="relative group max-w-[240px] mx-auto">
          <img
            src={currentImage}
            alt={`${title} - preview ${activeImageIndex + 1}`}
            className="w-48 h-48 mx-auto object-cover rounded-xl shadow-lg transition-all duration-300"
          />
          {galleryImages.length > 1 && (
            <>
              <button
                onClick={() => setActiveImageIndex((prev) => (prev > 0 ? prev - 1 : galleryImages.length - 1))}
                className="absolute left-0 top-1/2 -translate-y-1/2 p-1.5 rounded-full bg-slate-900/80 text-slate-300 hover:text-white border border-slate-700/80 backdrop-blur-sm transition-all"
                title="Предыдущее фото"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                onClick={() => setActiveImageIndex((prev) => (prev < galleryImages.length - 1 ? prev + 1 : 0))}
                className="absolute right-0 top-1/2 -translate-y-1/2 p-1.5 rounded-full bg-slate-900/80 text-slate-300 hover:text-white border border-slate-700/80 backdrop-blur-sm transition-all"
                title="Следующее фото"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </>
          )}
        </div>

        {/* Thumbnail Selector Bar */}
        {galleryImages.length > 1 && (
          <div className="flex items-center justify-center gap-2 overflow-x-auto pt-1 pb-1 scrollbar-none">
            {galleryImages.map((img, idx) => (
              <button
                key={idx}
                onClick={() => setActiveImageIndex(idx)}
                className={`relative rounded-lg overflow-hidden border-2 transition-all ${
                  activeImageIndex === idx
                    ? 'border-cyan-500 scale-105 shadow-md shadow-cyan-500/30'
                    : 'border-slate-800 opacity-60 hover:opacity-100 hover:border-slate-600'
                }`}
              >
                <img src={img} alt={`thumb-${idx}`} className="w-10 h-10 object-cover" />
              </button>
            ))}
          </div>
        )}

        <div className="space-y-1 pt-1">
          <span className="text-[10px] text-cyan-400 uppercase tracking-widest font-semibold">{brand}</span>
          <h1 className="text-base font-extrabold text-slate-100">
            {title}
          </h1>
        </div>
      </div>

      {/* Dynamic Offers Matrix Table */}
      <div className="glass-panel rounded-2xl p-4 border border-slate-800 space-y-3">
        <h3 className="text-sm font-bold text-slate-100 flex items-center justify-between">
          <span>Сравнение предложений ({sortedOffers.length})</span>
          <span className="text-xs text-slate-400 font-normal">Доставка во Вьетнам 🇻🇳</span>
        </h3>

        <div className="space-y-2">
          {sortedOffers.map((offer, idx) => {
            const cfg = PLATFORM_CONFIG[offer.platform] || {
              label: offer.platform.toUpperCase(),
              color: 'bg-cyan-500',
              btnBg: 'bg-cyan-600',
              hoverBg: 'hover:bg-cyan-500'
            };
            const isBest = offer.price === minPrice;
            const offerUrl = offer.url || getMarketplaceLink(offer.platform);

            return (
              <div
                key={idx}
                className={`flex items-center justify-between p-3 rounded-xl bg-slate-900 border ${
                  isBest ? 'border-emerald-500/40' : 'border-slate-800'
                }`}
              >
                <div>
                  <div className="text-xs font-bold text-slate-100 flex items-center gap-1.5">
                    {cfg.label}
                    {isBest && (
                      <span className="rounded bg-emerald-500/20 px-1.5 py-0.5 text-[9px] text-emerald-400 font-bold">
                        ЛУЧШАЯ ЦЕНА
                      </span>
                    )}
                    {cfg.badge && (
                      <span className="flex items-center gap-0.5 rounded bg-violet-500/20 px-1.5 py-0.5 text-[8px] font-bold text-violet-300">
                        <Zap className="w-2.5 h-2.5" />{cfg.badge}
                      </span>
                    )}
                  </div>
                  <div className="text-[11px] text-slate-400">
                    {offer.delivery_info || 'Доставка во Вьетнам: 1-3 дня'}
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <div className="text-right">
                    <div className={`text-sm font-extrabold ${isBest ? 'text-emerald-400' : 'text-slate-100'}`}>
                      {offer.price.toLocaleString()} ₫
                    </div>
                    {offer.old_price && offer.old_price > offer.price && (
                      <div className="text-[10px] text-slate-500 line-through">
                        {offer.old_price.toLocaleString()} ₫
                      </div>
                    )}
                  </div>
                  <a
                    href={offerUrl}
                    target="_blank"
                    rel="noreferrer"
                    className={`flex items-center gap-1 rounded-lg px-3 py-1.5 text-xs font-bold text-white transition-all ${cfg.btnBg} ${cfg.hoverBg}`}
                  >
                    Купить <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* PVZ Delivery Options Card */}
      <div className="glass-panel rounded-2xl p-4 border border-cyan-500/30 bg-gradient-to-b from-cyan-950/20 to-slate-900 space-y-3">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-cyan-500/20 text-cyan-400">
            <Package className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-extrabold text-slate-100 flex items-center gap-1.5">
              Доставка в ПВЗ SmartSearch 🇻🇳
              <span className="rounded bg-emerald-500/20 px-1.5 py-0.5 text-[9px] font-extrabold text-emerald-400">
                Нячанг • Дананг • Сайгон
              </span>
            </h3>
            <p className="text-[11px] text-slate-400">Выберите удобный способ получения вашей посылки:</p>
          </div>
        </div>

        {/* Action Buttons: Primary & Secondary */}
        <div className="space-y-2 pt-1">
          {/* PRIMARY: Buy via PVZ */}
          <button
            onClick={() => setShowPvzModal(true)}
            className="w-full rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 p-3 text-xs font-extrabold text-white shadow-lg glow-cyan flex items-center justify-center gap-2 hover:opacity-95 transition-all"
          >
            <ShoppingBag className="w-4 h-4" />
            1. Выкупить с доставкой в ПВЗ (Основной способ)
          </button>

          {/* SECONDARY: Self Order to PVZ address */}
          <button
            onClick={() => setShowPvzModal(true)}
            className="w-full rounded-xl bg-slate-900 border border-slate-700 p-2.5 text-xs font-bold text-slate-300 hover:text-white hover:bg-slate-800 flex items-center justify-center gap-2 transition-all"
          >
            <Copy className="w-3.5 h-3.5 text-cyan-400" />
            2. Скопировать адрес ПВЗ для своего заказа
          </button>
        </div>
      </div>

      {/* Interactive Price History Chart (MOVED TO THE BOTTOM) */}
      <div className="glass-panel rounded-2xl p-4 border border-slate-800 space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-xs text-slate-400 font-medium">Динамика цен (Нячанг 🇻🇳)</div>
            <div className="text-lg font-black text-emerald-400">7 490 000 ₫ <span className="text-xs font-normal text-slate-500">(-16%)</span></div>
          </div>
          <div className="flex gap-1 bg-slate-900 p-1 rounded-lg border border-slate-800 text-[11px]">
            {['1M', '3M', '6M', '1Y'].map((period) => (
              <button
                key={period}
                onClick={() => setSelectedPeriod(period.toLowerCase())}
                className={`px-2.5 py-1 rounded-md font-semibold transition-all ${
                  selectedPeriod === period.toLowerCase()
                    ? 'bg-cyan-500 text-white shadow-sm'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                {period}
              </button>
            ))}
          </div>
        </div>

        <div className="h-44 w-full pt-2">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={[
              { date: '01 Мая', minPrice: 8900000 },
              { date: '15 Мая', minPrice: 8500000 },
              { date: '01 Июня', minPrice: 8100000 },
              { date: '15 Июня', minPrice: 7800000 },
              { date: '01 Июля', minPrice: 7650000 },
              { date: '01 Авг', minPrice: 7490000 },
            ]}>
              <defs>
                <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.4}/>
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0.0}/>
                </linearGradient>
              </defs>
              <XAxis dataKey="date" stroke="#64748b" fontSize={10} tickLine={false} />
              <YAxis stroke="#64748b" fontSize={10} tickLine={false} domain={['auto', 'auto']} hide />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                formatter={(val: number) => [`${val.toLocaleString()} ₫`, 'Минимальная цена']}
              />
              <Area type="monotone" dataKey="minPrice" stroke="#10b981" strokeWidth={2.5} fillOpacity={1} fill="url(#colorPrice)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Sticky Bottom Alert Button */}
      <div className="fixed bottom-16 left-4 right-4 z-40">
        <button
          onClick={() => setShowAlertModal(true)}
          className="w-full rounded-xl bg-slate-900 border border-slate-800 p-3 text-xs font-bold text-slate-300 shadow-xl flex items-center justify-center gap-2 hover:text-white hover:border-slate-700 transition-all"
        >
          <Bell className="w-4 h-4 text-amber-400" />
          {isAlertCreated ? 'Алерт активен! Изменить цену' : 'Следить за ценой (Уведомить о скидке)'}
        </button>
      </div>

      {/* PVZ Modal */}
      {showPvzModal && (
        <PvzModal
          product={{
            title: title,
            price: minPrice || 7490000,
            currency: 'VND',
            platform: sortedOffers[0]?.platform || 'shopee',
            product_url: sortedOffers[0]?.url || getMarketplaceLink('shopee'),
            image_url: image,
          }}
          onClose={() => setShowPvzModal(false)}
        />
      )}

      {/* Price Alert Bottom Modal */}
      {showAlertModal && (
        <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/70 backdrop-blur-sm p-4 animate-in fade-in">
          <div className="w-full max-w-md rounded-2xl bg-slate-900 p-5 border border-slate-800 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <Bell className="w-4 h-4 text-cyan-400" /> Настройка Алерта Цены
              </h3>
              <button onClick={() => setShowAlertModal(false)} className="text-slate-500 hover:text-white text-sm font-bold">✕</button>
            </div>

            <div className="space-y-2">
              <label className="text-xs text-slate-400">Прислать push-уведомление в Бот, когда цена упадет ниже:</label>
              <div className="relative">
                <input
                  type="number"
                  value={targetPrice}
                  onChange={(e) => setTargetPrice(e.target.value)}
                  className="w-full rounded-xl bg-slate-950 border border-slate-800 p-3 text-base font-extrabold text-emerald-400 focus:border-cyan-500 focus:outline-none"
                />
                <span className="absolute right-4 top-3 text-sm font-bold text-slate-500">₫</span>
              </div>
            </div>

            <button
              onClick={handleCreateAlert}
              className="w-full rounded-xl bg-cyan-600 py-3 text-sm font-bold text-white hover:bg-cyan-500 shadow-md"
            >
              Создать подписку
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
