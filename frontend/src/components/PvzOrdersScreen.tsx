import React, { useState, useEffect } from 'react';
import { Package, Clock, CheckCircle2, MapPin, Truck, RefreshCw, AlertCircle, QrCode } from 'lucide-react';

interface PvzOrdersScreenProps {
  onSelectProduct?: (id: string) => void;
}

export const PvzOrdersScreen: React.FC<PvzOrdersScreenProps> = () => {
  const [orders, setOrders] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchOrders = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/v1/pvz/orders?user_telegram_id=demo_user');
      if (res.ok) {
        const data = await res.json();
        setOrders(data);
      }
    } catch (e) {
      console.log('Using default mock orders');
      setOrders([
        {
          id: 'ord_88412',
          pvz_name: 'ПВЗ Нячанг (Центральный)',
          product_title: 'Беспроводные полноразмерные наушники Sony WH-1000XM5 Black',
          image_url: 'https://down-vn.img.susercontent.com/file/vn-11134207-7r98o-ls530z22z4a01c',
          platform: 'shopee',
          price: 7490000.0,
          currency: 'VND',
          recipient_name: 'Игорь Филов',
          delivery_method: 'buy_for_me',
          pickup_code: 'PVZ-8841',
          tracking_number: 'SPX-VN-9081234',
          status: 'in_transit',
          created_at: '2026-08-05T14:30:00Z',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
  }, []);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'ready':
        return (
          <span className="flex items-center gap-1 rounded-full bg-emerald-500/20 px-2.5 py-0.5 text-[10px] font-extrabold text-emerald-400 border border-emerald-500/40">
            <CheckCircle2 className="w-3 h-3" /> ГОТОВ К ВЫДАЧЕ В ПВЗ
          </span>
        );
      case 'in_transit':
        return (
          <span className="flex items-center gap-1 rounded-full bg-cyan-500/20 px-2.5 py-0.5 text-[10px] font-extrabold text-cyan-400 border border-cyan-500/40">
            <Truck className="w-3 h-3 animate-pulse" /> В ПУТИ НА ПВЗ
          </span>
        );
      case 'purchased':
        return (
          <span className="flex items-center gap-1 rounded-full bg-purple-500/20 px-2.5 py-0.5 text-[10px] font-extrabold text-purple-300 border border-purple-500/40">
            <Package className="w-3 h-3" /> ВЫКУПЛЕН ОПЕРАТОРОМ
          </span>
        );
      default:
        return (
          <span className="flex items-center gap-1 rounded-full bg-amber-500/20 px-2.5 py-0.5 text-[10px] font-extrabold text-amber-300 border border-amber-500/40">
            <Clock className="w-3 h-3" /> ОЖИДАЕТ ОБРАБОТКИ
          </span>
        );
    }
  };

  return (
    <div className="space-y-4 pb-28 pt-2">
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-black text-slate-100 flex items-center gap-2">
            <Package className="w-5 h-5 text-cyan-400" /> Мои Заказы в ПВЗ
          </h1>
          <p className="text-xs text-slate-400">Отслеживание доставляемых товаров</p>
        </div>
        <button
          onClick={fetchOrders}
          className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Orders List */}
      {orders.length === 0 ? (
        <div className="glass-panel rounded-2xl p-8 border border-slate-800 text-center space-y-3">
          <Package className="w-10 h-10 mx-auto text-slate-600" />
          <p className="text-sm font-semibold text-slate-400">У вас пока нет активных заказов в ПВЗ</p>
          <p className="text-xs text-slate-500">
            Выберите товар в поиске и нажмите «Выкупить с доставкой в ПВЗ»
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {orders.map((order) => (
            <div
              key={order.id}
              className="glass-panel rounded-2xl p-4 border border-slate-800 space-y-3 hover:border-slate-700 transition-all"
            >
              {/* Status Header */}
              <div className="flex items-center justify-between border-b border-slate-800/80 pb-2.5">
                {getStatusBadge(order.status)}
                <span className="font-mono text-xs font-black text-slate-300">
                  ПИН: <span className="text-cyan-400">{order.pickup_code}</span>
                </span>
              </div>

              {/* Product Info */}
              <div className="flex gap-3 items-center">
                <img
                  src={order.image_url}
                  alt={order.product_title}
                  className="w-14 h-14 object-cover rounded-xl border border-slate-800"
                />
                <div className="space-y-1 flex-1 min-w-0">
                  <div className="text-xs font-bold text-slate-100 truncate">{order.product_title}</div>
                  <div className="text-[11px] text-slate-400 flex items-center gap-1">
                    <MapPin className="w-3 h-3 text-cyan-400" /> {order.pvz_name}
                  </div>
                  {order.price > 0 && (
                    <div className="text-xs font-extrabold text-emerald-400">
                      {order.price.toLocaleString()} {order.currency}
                    </div>
                  )}
                </div>
              </div>

              {/* Order Footer & Pickup Details */}
              <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-800/60 flex items-center justify-between text-xs">
                <div className="text-[11px] text-slate-400">
                  <span>Способ: </span>
                  <span className="font-semibold text-slate-200">
                    {order.delivery_method === 'buy_for_me' ? 'Выкуп через ПВЗ' : 'Самостоятельный заказ'}
                  </span>
                </div>
                {order.tracking_number && (
                  <div className="font-mono text-[10px] text-cyan-300/80">
                    Трек: {order.tracking_number}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
