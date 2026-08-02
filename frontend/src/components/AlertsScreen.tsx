import React from 'react';
import { Bell, Trash2, TrendingDown, CheckCircle2 } from 'lucide-react';

interface AlertsScreenProps {
  onSelectProduct: (productId: string) => void;
}

export const AlertsScreen: React.FC<AlertsScreenProps> = ({ onSelectProduct }) => {
  const activeAlerts = [
    {
      id: 'alert_1',
      masterId: 'mst_9f83a210',
      title: 'Sony WH-1000XM5 Black',
      targetPrice: 27000,
      currentMinPrice: 28990,
      image: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&q=80',
      platform: 'Ozon'
    },
    {
      id: 'alert_2',
      masterId: 'mst_macbook_m3',
      title: 'Apple MacBook Air 15" M3',
      targetPrice: 115000,
      currentMinPrice: 118400,
      image: 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400&q=80',
      platform: 'WB'
    }
  ];

  return (
    <div className="space-y-4 pb-24 pt-2">
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
        <h1 className="text-lg font-bold text-slate-100 flex items-center gap-2">
          <Bell className="w-5 h-5 text-cyan-400" />
          Мои подписки на цены ({activeAlerts.length})
        </h1>
      </div>

      <div className="space-y-3">
        {activeAlerts.map((alert) => (
          <div
            key={alert.id}
            className="glass-panel relative flex items-center gap-3.5 rounded-xl p-3.5 border border-slate-800 hover:border-cyan-500/40 transition-all"
          >
            <img
              src={alert.image}
              alt={alert.title}
              onClick={() => onSelectProduct(alert.masterId)}
              className="w-16 h-16 rounded-lg object-cover bg-slate-800 cursor-pointer"
            />
            <div className="flex-1 min-w-0 space-y-1">
              <h3
                onClick={() => onSelectProduct(alert.masterId)}
                className="text-xs font-bold text-slate-100 truncate cursor-pointer hover:text-cyan-400"
              >
                {alert.title}
              </h3>
              <div className="flex items-center gap-3 text-xs">
                <div>
                  <span className="text-[10px] text-slate-500 block">Целевая цена:</span>
                  <span className="font-extrabold text-cyan-400">{alert.targetPrice.toLocaleString()} ₽</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 block">Текущая мин:</span>
                  <span className="font-bold text-slate-300">{alert.currentMinPrice.toLocaleString()} ₽</span>
                </div>
              </div>
            </div>

            <button className="p-2 text-slate-500 hover:text-rose-400 transition-colors">
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};
