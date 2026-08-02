import React, { useState } from 'react';
import { ArrowLeft, Bell, Heart, ExternalLink, ShieldCheck, TrendingDown, Star } from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip } from 'recharts';

interface ProductDetailScreenProps {
  productId: string;
  onBack: () => void;
}

export const ProductDetailScreen: React.FC<ProductDetailScreenProps> = ({ productId, onBack }) => {
  const [selectedPeriod, setSelectedPeriod] = useState('3m');
  const [showAlertModal, setShowAlertModal] = useState(false);
  const [targetPrice, setTargetPrice] = useState('27000');
  const [isAlertCreated, setIsAlertCreated] = useState(false);

  const priceHistoryData = [
    { date: '01 Мая', minPrice: 33500 },
    { date: '15 Мая', minPrice: 32900 },
    { date: '01 Июня', minPrice: 31000 },
    { date: '15 Июня', minPrice: 29500 },
    { date: '01 Июля', minPrice: 29400 },
    { date: '01 Авг', minPrice: 28990 },
  ];

  const handleCreateAlert = () => {
    if (window.Telegram?.WebApp?.HapticFeedback) {
      window.Telegram.WebApp.HapticFeedback.notificationOccurred('success');
    }
    setIsAlertCreated(true);
    setShowAlertModal(false);
  };

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

      {/* Main Image Banner */}
      <div className="glass-panel relative rounded-2xl p-4 border border-slate-800 text-center space-y-3">
        <img
          src="https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&q=80"
          alt="Sony WH-1000XM5"
          className="w-48 h-48 mx-auto object-cover rounded-xl shadow-lg"
        />
        <div className="space-y-1">
          <span className="text-[10px] text-cyan-400 uppercase tracking-widest font-semibold">Sony • Электроника</span>
          <h1 className="text-base font-extrabold text-slate-100">
            Беспроводные полноразмерные наушники Sony WH-1000XM5 Black
          </h1>
        </div>
      </div>

      {/* Interactive Price History Chart */}
      <div className="glass-panel rounded-2xl p-4 border border-slate-800 space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-xs text-slate-400 font-medium">Динамика цен</div>
            <div className="text-lg font-black text-emerald-400">28 990 ₽ <span className="text-xs font-normal text-slate-500">(-13%)</span></div>
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
            <AreaChart data={priceHistoryData}>
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
                formatter={(val: number) => [`${val.toLocaleString()} ₽`, 'Минимальная цена']}
              />
              <Area type="monotone" dataKey="minPrice" stroke="#10b981" strokeWidth={2.5} fillOpacity={1} fill="url(#colorPrice)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Offers Matrix Table */}
      <div className="glass-panel rounded-2xl p-4 border border-slate-800 space-y-3">
        <h3 className="text-sm font-bold text-slate-100 flex items-center justify-between">
          <span>Сравнение предложений ({3})</span>
          <span className="text-xs text-slate-400 font-normal">С учетом СПП & Скидок</span>
        </h3>

        <div className="space-y-2">
          <div className="flex items-center justify-between p-3 rounded-xl bg-slate-900 border border-emerald-500/40">
            <div>
              <div className="text-xs font-bold text-slate-100 flex items-center gap-1.5">
                Ozon Seller
                <span className="rounded bg-emerald-500/20 px-1.5 py-0.5 text-[9px] text-emerald-400 font-bold">ТОП ЦЕНА</span>
              </div>
              <div className="text-[11px] text-slate-400">Доставка: 1-2 дня</div>
            </div>
            <div className="flex items-center gap-3">
              <div className="text-right">
                <div className="text-sm font-extrabold text-emerald-400">28 990 ₽</div>
                <div className="text-[10px] text-slate-500 line-through">35 000 ₽</div>
              </div>
              <a
                href="https://ozon.ru"
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-1 rounded-lg bg-blue-600 px-3 py-1.5 text-xs font-bold text-white hover:bg-blue-500"
              >
                Купить <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          </div>

          <div className="flex items-center justify-between p-3 rounded-xl bg-slate-900 border border-slate-800">
            <div>
              <div className="text-xs font-bold text-slate-100">Wildberries Seller</div>
              <div className="text-[11px] text-slate-400">Доставка: Завтра</div>
            </div>
            <div className="flex items-center gap-3">
              <div className="text-right">
                <div className="text-sm font-extrabold text-slate-100">29 400 ₽</div>
                <div className="text-[10px] text-slate-500 line-through">32 000 ₽</div>
              </div>
              <a
                href="https://wildberries.ru"
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-1 rounded-lg bg-purple-600 px-3 py-1.5 text-xs font-bold text-white hover:bg-purple-500"
              >
                Купить <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Sticky Bottom Main Button Simulated */}
      <div className="fixed bottom-16 left-4 right-4 z-40">
        <button
          onClick={() => setShowAlertModal(true)}
          className="w-full rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 p-3.5 text-sm font-extrabold text-white shadow-xl glow-cyan flex items-center justify-center gap-2 hover:opacity-95 transition-all"
        >
          <Bell className="w-4 h-4" />
          {isAlertCreated ? 'Алерт активен! Изменить цену' : 'Следить за ценой (Уведомить о скидке)'}
        </button>
      </div>

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
                <span className="absolute right-4 top-3 text-sm font-bold text-slate-500">₽</span>
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
