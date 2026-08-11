import React, { useState, useEffect } from 'react';
import { Bell, Trash2, Heart, ExternalLink, CheckCircle2, ShoppingBag } from 'lucide-react';

interface AlertsScreenProps {
  onSelectProduct: (productId: string) => void;
}

const API_BASE = (import.meta as any).env?.VITE_API_URL || '';

export const AlertsScreen: React.FC<AlertsScreenProps> = ({ onSelectProduct }) => {
  const [activeTab, setActiveTab] = useState<'alerts' | 'favorites'>('alerts');
  const [alerts, setAlerts] = useState<any[]>([
    {
      id: 'alert_1',
      masterId: 'mst_9f83a210',
      title: 'Sony WH-1000XM5 Black',
      targetPrice: 7000000,
      currentMinPrice: 7490000,
      image: 'https://down-vn.img.susercontent.com/file/vn-11134207-7r98o-ls530z22z4a01c',
      platform: 'Shopee VN'
    },
    {
      id: 'alert_2',
      masterId: 'mst_macbook_m3',
      title: 'Apple MacBook Air 15" M3',
      targetPrice: 26000000,
      currentMinPrice: 27990000,
      image: 'https://vn-live-01.slatic.net/p/3b1236f014e7ee87db5a31a980753b8f.jpg',
      platform: 'Lazada VN'
    }
  ]);
  const [favorites, setFavorites] = useState<any[]>([]);
  const [deletedNotice, setDeletedNotice] = useState<string | null>(null);

  useEffect(() => {
    // Fetch user alerts from backend API
    async function loadAlerts() {
      try {
        const res = await fetch(`${API_BASE}/api/v1/alerts`);
        if (res.ok) {
          const data = await res.json();
          if (Array.isArray(data) && data.length > 0) {
            const formatted = data.map((a: any) => ({
              id: a.alert_id,
              masterId: a.master_id,
              title: `Отслеживаемый товар (${a.master_id.slice(0, 8)})`,
              targetPrice: a.target_price,
              currentMinPrice: a.target_price * 1.05,
              image: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&q=80',
              platform: 'Shopee VN'
            }));
            setAlerts(formatted);
          }
        }
      } catch (e) {
        console.error('Failed to load alerts from API:', e);
      }
    }

    // Fetch favorites from localStorage
    function loadFavorites() {
      try {
        const stored = localStorage.getItem('smartsearch_favorites');
        if (stored) {
          setFavorites(JSON.parse(stored));
        } else {
          setFavorites([
            {
              id: 'mst_9f83a210',
              master_id: 'mst_9f83a210',
              title: 'Sony WH-1000XM5 Black',
              brand: 'Sony',
              price: 7490000,
              image: 'https://down-vn.img.susercontent.com/file/vn-11134207-7r98o-ls530z22z4a01c',
            }
          ]);
        }
      } catch (e) {
        console.error('Failed to load favorites:', e);
      }
    }

    loadAlerts();
    loadFavorites();
  }, []);

  const handleDeleteAlert = async (id: string, title: string) => {
    if (window.Telegram?.WebApp?.HapticFeedback) {
      window.Telegram.WebApp.HapticFeedback.notificationOccurred('success');
    }

    setAlerts(prev => prev.filter(a => a.id !== id));
    setDeletedNotice(`Алерт на "${title}" удален`);
    setTimeout(() => setDeletedNotice(null), 2500);

    try {
      await fetch(`${API_BASE}/api/v1/alerts/${id}`, { method: 'DELETE' });
    } catch (e) {
      console.error('Error deleting alert:', e);
    }
  };

  const handleDeleteFavorite = (id: string, title: string) => {
    if (window.Telegram?.WebApp?.HapticFeedback) {
      window.Telegram.WebApp.HapticFeedback.notificationOccurred('success');
    }

    const updated = favorites.filter(f => f.id !== id && f.master_id !== id);
    setFavorites(updated);
    localStorage.setItem('smartsearch_favorites', JSON.stringify(updated));

    setDeletedNotice(`Товар "${title}" удален из Избранного`);
    setTimeout(() => setDeletedNotice(null), 2500);
  };

  return (
    <div className="space-y-4 pb-24 pt-2">
      {/* Header with Dual Tabs */}
      <div className="space-y-3 border-b border-slate-800/80 pb-3">
        <div className="flex items-center justify-between">
          <h1 className="text-lg font-extrabold text-slate-100 flex items-center gap-2">
            {activeTab === 'alerts' ? (
              <>
                <Bell className="w-5 h-5 text-cyan-400" /> Мои подписки на цены ({alerts.length})
              </>
            ) : (
              <>
                <Heart className="w-5 h-5 text-rose-400 fill-rose-400" /> Избранные товары ({favorites.length})
              </>
            )}
          </h1>
        </div>

        {/* Tab Switcher */}
        <div className="grid grid-cols-2 gap-2 bg-slate-900 p-1.5 rounded-2xl border border-slate-800 text-xs font-bold">
          <button
            onClick={() => setActiveTab('alerts')}
            className={`py-2 rounded-xl transition-all flex items-center justify-center gap-1.5 ${
              activeTab === 'alerts'
                ? 'bg-cyan-500 text-white shadow-md'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Bell className="w-3.5 h-3.5" /> Мои Алерты ({alerts.length})
          </button>
          <button
            onClick={() => setActiveTab('favorites')}
            className={`py-2 rounded-xl transition-all flex items-center justify-center gap-1.5 ${
              activeTab === 'favorites'
                ? 'bg-rose-500 text-white shadow-md'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Heart className="w-3.5 h-3.5" /> Избранное ({favorites.length})
          </button>
        </div>
      </div>

      {/* Delete Notification Banner */}
      {deletedNotice && (
        <div className="rounded-xl bg-rose-500/20 border border-rose-500/40 p-3 text-xs font-bold text-rose-300 flex items-center gap-2 animate-in fade-in">
          <CheckCircle2 className="w-4 h-4 text-rose-400" />
          {deletedNotice}
        </div>
      )}

      {/* TAB 1: ALERTS LIST */}
      {activeTab === 'alerts' && (
        <div className="space-y-3">
          {alerts.map((alert) => (
            <div
              key={alert.id}
              className="glass-panel relative flex items-center gap-3.5 rounded-2xl p-3.5 border border-slate-800 hover:border-cyan-500/40 transition-all"
            >
              <img
                src={alert.image}
                alt={alert.title}
                onClick={() => onSelectProduct(alert.masterId)}
                className="w-16 h-16 rounded-xl object-cover bg-slate-800 cursor-pointer"
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
                    <span className="font-extrabold text-cyan-400">{alert.targetPrice?.toLocaleString()} ₫</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-500 block">Текущая:</span>
                    <span className="font-bold text-slate-300">{alert.currentMinPrice?.toLocaleString()} ₫</span>
                  </div>
                </div>
              </div>

              <button
                onClick={() => handleDeleteAlert(alert.id, alert.title)}
                className="p-2 text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 rounded-xl transition-all"
                title="Удалить алерт"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}

          {alerts.length === 0 && (
            <div className="text-center py-12 text-slate-500 space-y-2">
              <Bell className="w-10 h-10 mx-auto opacity-30" />
              <p className="text-sm font-semibold">У вас нет активных алертов</p>
              <p className="text-xs text-slate-400">Нажмите на колокольчик на карточке товара, чтобы следить за скидками.</p>
            </div>
          )}
        </div>
      )}

      {/* TAB 2: FAVORITES LIST */}
      {activeTab === 'favorites' && (
        <div className="space-y-3">
          {favorites.map((fav) => (
            <div
              key={fav.id || fav.master_id}
              className="glass-panel relative flex items-center gap-3.5 rounded-2xl p-3.5 border border-slate-800 hover:border-rose-500/40 transition-all"
            >
              <img
                src={fav.image || 'https://down-vn.img.susercontent.com/file/vn-11134207-7r98o-ls530z22z4a01c'}
                alt={fav.title}
                onClick={() => onSelectProduct(fav.id || fav.master_id)}
                className="w-16 h-16 rounded-xl object-cover bg-slate-800 cursor-pointer"
              />
              <div className="flex-1 min-w-0 space-y-1">
                {fav.brand && <span className="text-[9px] text-rose-400 font-bold uppercase">{fav.brand}</span>}
                <h3
                  onClick={() => onSelectProduct(fav.id || fav.master_id)}
                  className="text-xs font-bold text-slate-100 truncate cursor-pointer hover:text-rose-400"
                >
                  {fav.title}
                </h3>
                <div className="text-xs font-extrabold text-emerald-400">
                  {fav.price ? fav.price.toLocaleString() : '7 490 000'} ₫
                </div>
              </div>

              <button
                onClick={() => handleDeleteFavorite(fav.id || fav.master_id, fav.title)}
                className="p-2 text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 rounded-xl transition-all"
                title="Удалить из избранного"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}

          {favorites.length === 0 && (
            <div className="text-center py-12 text-slate-500 space-y-2">
              <Heart className="w-10 h-10 mx-auto opacity-30" />
              <p className="text-sm font-semibold">Список избранного пуст</p>
              <p className="text-xs text-slate-400">Нажмите на сердечко на экране товара, чтобы сохранить его здесь.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
