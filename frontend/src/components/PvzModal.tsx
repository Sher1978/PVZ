import React, { useState } from 'react';
import { Package, Copy, Check, MapPin, Phone, ShieldCheck, ShoppingBag, ExternalLink, QrCode } from 'lucide-react';

interface PvzModalProps {
  product: {
    title: string;
    price: number;
    currency: string;
    platform: string;
    product_url: string;
    image_url?: string;
  };
  onClose: () => void;
  onOrderCreated?: (order: any) => void;
}

const PVZ_POINTS = [
  {
    id: 'pvz_nhatrang_01',
    city: 'Nha Trang 🇻🇳',
    name: 'ПВЗ Нячанг (Центральный)',
    address_vn: '123 Nguyễn Thiện Thuật, Phường Tân Lập, TP. Nha Trang, Khánh Hòa',
    address_en: '123 Nguyen Thien Thuat, Tan Lap, Nha Trang, Khanh Hoa',
    hours: 'Ежедневно: 09:00 – 21:00',
    phone: '+84 90 512 34 56',
  },
  {
    id: 'pvz_danang_01',
    city: 'Da Nang 🇻🇳',
    name: 'ПВЗ Дананг (Хайчау)',
    address_vn: '45 Nguyễn Văn Linh, Phường Nam Dương, Quận Hải Châu, Đà Nẵng',
    address_en: '45 Nguyen Van Linh, Nam Duong, Hai Chau, Da Nang',
    hours: 'Ежедневно: 09:00 – 20:00',
    phone: '+84 90 678 90 12',
  },
  {
    id: 'pvz_saigon_01',
    city: 'Ho Chi Minh City 🇻🇳',
    name: 'ПВЗ Сайгон (Район 1)',
    address_vn: '88 Lê Lợi, Phường Bến Thành, Quận 1, TP. Hồ Chí Minh',
    address_en: '88 Le Loi, Ben Thanh, District 1, Ho Chi Minh City',
    hours: 'Ежедневно: 08:30 – 21:30',
    phone: '+84 90 111 22 33',
  },
];

export const PvzModal: React.FC<PvzModalProps> = ({ product, onClose, onOrderCreated }) => {
  const [activeTab, setActiveTab] = useState<'buy_for_me' | 'self_order'>('buy_for_me');
  const [selectedPvzId, setSelectedPvzId] = useState(PVZ_POINTS[0].id);
  const [recipientName, setRecipientName] = useState('Игорь Филов');
  const [recipientPhone, setRecipientPhone] = useState('+84 912 345 678');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [createdOrder, setCreatedOrder] = useState<any>(null);
  const [copiedField, setCopiedField] = useState<string | null>(null);

  const currentPvz = PVZ_POINTS.find((p) => p.id === selectedPvzId) || PVZ_POINTS[0];
  const personalShippingId = '#SS-8841-VN';

  const handleCopy = (text: string, fieldName: string) => {
    navigator.clipboard.writeText(text);
    setCopiedField(fieldName);
    if (window.Telegram?.WebApp?.HapticFeedback) {
      window.Telegram.WebApp.HapticFeedback.notificationOccurred('success');
    }
    setTimeout(() => setCopiedField(null), 2000);
  };

  const handleCreateOrder = async () => {
    setIsSubmitting(true);
    if (window.Telegram?.WebApp?.HapticFeedback) {
      window.Telegram.WebApp.HapticFeedback.impactOccurred('medium');
    }

    try {
      const response = await fetch('/api/v1/pvz/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_telegram_id: 'demo_user',
          pvz_id: currentPvz.id,
          product_title: product.title,
          product_url: product.product_url,
          image_url: product.image_url,
          platform: product.platform,
          price: product.price,
          currency: product.currency,
          recipient_name: recipientName,
          recipient_phone: recipientPhone,
          delivery_method: 'buy_for_me',
        }),
      });

      if (!response.ok) throw new Error('Order creation failed');
      const order = await response.json();
      setCreatedOrder(order);
      if (onOrderCreated) onOrderCreated(order);
    } catch (e) {
      // Fallback local mock if backend offline
      const mockOrder = {
        id: `ord_${Math.floor(Math.random() * 90000) + 10000}`,
        pickup_code: `PVZ-${Math.floor(Math.random() * 9000) + 1000}`,
        pvz_name: currentPvz.name,
        product_title: product.title,
        price: product.price,
        currency: product.currency,
        recipient_name: recipientName,
        status: 'pending',
      };
      setCreatedOrder(mockOrder);
      if (onOrderCreated) onOrderCreated(mockOrder);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/80 backdrop-blur-md p-3 animate-in fade-in">
      <div className="w-full max-w-lg rounded-3xl bg-slate-900 border border-slate-800 p-5 space-y-4 shadow-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
              <Package className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-extrabold text-slate-100">Доставка на ПВЗ SmartSearch</h3>
              <p className="text-[11px] text-slate-400">Выдаём посылки во Вьетнаме 🇻🇳</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-slate-800 text-slate-400 hover:text-white flex items-center justify-center font-bold"
          >
            ✕
          </button>
        </div>

        {createdOrder ? (
          /* Order Confirmation Screen */
          <div className="space-y-4 text-center py-3">
            <div className="w-16 h-16 mx-auto rounded-full bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 flex items-center justify-center">
              <ShieldCheck className="w-8 h-8" />
            </div>
            <div>
              <span className="inline-block rounded-full bg-emerald-500/20 px-3 py-1 text-xs font-extrabold text-emerald-400 mb-1">
                ЗАКАЗ УСПЕШНО ОФОРМЛЕН
              </span>
              <h2 className="text-lg font-black text-white">ПИН-код выдачи: {createdOrder.pickup_code}</h2>
              <p className="text-xs text-slate-400 mt-1">
                Оператор ПВЗ уже принял заказ в обработку. Сохраните этот ПИН-код для получения.
              </p>
            </div>

            <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 text-left space-y-2 text-xs">
              <div className="flex justify-between text-slate-400">
                <span>ПВЗ:</span> <span className="font-semibold text-slate-200">{createdOrder.pvz_name}</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Получатель:</span> <span className="font-semibold text-slate-200">{createdOrder.recipient_name}</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Сумма предоплаты (100%):</span>{' '}
                <span className="font-extrabold text-emerald-400">
                  {createdOrder.price?.toLocaleString()} {createdOrder.currency}
                </span>
              </div>
            </div>

            <button
              onClick={onClose}
              className="w-full rounded-xl bg-cyan-500 py-3 text-xs font-bold text-white hover:bg-cyan-400"
            >
              Перейти к Моим Заказам
            </button>
          </div>
        ) : (
          <>
            {/* Dual Tabs selection */}
            <div className="grid grid-cols-2 gap-2 bg-slate-950 p-1.5 rounded-2xl border border-slate-800 text-xs font-bold">
              <button
                onClick={() => setActiveTab('buy_for_me')}
                className={`py-2.5 rounded-xl transition-all flex items-center justify-center gap-1.5 ${
                  activeTab === 'buy_for_me'
                    ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-md'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <ShoppingBag className="w-3.5 h-3.5" />
                <span>1. Выкупить через ПВЗ (Основной)</span>
              </button>
              <button
                onClick={() => setActiveTab('self_order')}
                className={`py-2.5 rounded-xl transition-all flex items-center justify-center gap-1.5 ${
                  activeTab === 'self_order'
                    ? 'bg-gradient-to-r from-slate-800 to-slate-700 text-white shadow-md'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <Copy className="w-3.5 h-3.5" />
                <span>2. Свой заказ в ПВЗ</span>
              </button>
            </div>

            {/* TAB 1: BUY FOR ME (Primary Flow) */}
            {activeTab === 'buy_for_me' && (
              <div className="space-y-4 animate-in fade-in">
                {/* Select PVZ */}
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-300 flex items-center gap-1">
                    <MapPin className="w-3.5 h-3.5 text-cyan-400" /> Выберите пункт выдачи:
                  </label>
                  <select
                    value={selectedPvzId}
                    onChange={(e) => setSelectedPvzId(e.target.value)}
                    className="w-full rounded-xl bg-slate-950 border border-slate-800 p-2.5 text-xs font-semibold text-slate-100 focus:border-cyan-500 focus:outline-none"
                  >
                    {PVZ_POINTS.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.city} — {p.name}
                      </option>
                    ))}
                  </select>
                  <p className="text-[10px] text-slate-400 pl-1">{currentPvz.address_vn}</p>
                </div>

                {/* Contact Information */}
                <div className="grid grid-cols-2 gap-2">
                  <div className="space-y-1">
                    <label className="text-[11px] text-slate-400">ФИО получателя:</label>
                    <input
                      type="text"
                      value={recipientName}
                      onChange={(e) => setRecipientName(e.target.value)}
                      className="w-full rounded-xl bg-slate-950 border border-slate-800 p-2 text-xs font-semibold text-white focus:border-cyan-500 focus:outline-none"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-[11px] text-slate-400">Телефон (Zalo/WhatsApp):</label>
                    <input
                      type="text"
                      value={recipientPhone}
                      onChange={(e) => setRecipientPhone(e.target.value)}
                      className="w-full rounded-xl bg-slate-950 border border-slate-800 p-2 text-xs font-semibold text-white focus:border-cyan-500 focus:outline-none"
                    />
                  </div>
                </div>

                {/* Price Breakdown */}
                <div className="p-3 rounded-2xl bg-slate-950 border border-slate-800/90 space-y-1.5 text-xs">
                  <div className="flex justify-between text-slate-400">
                    <span>Товар ({product.platform.toUpperCase()}):</span>
                    <span className="font-semibold text-slate-200">
                      {product.price.toLocaleString()} {product.currency}
                    </span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>Обработка и хранение в ПВЗ:</span>
                    <span className="font-semibold text-emerald-400">БЕСПЛАТНО</span>
                  </div>
                  <div className="border-t border-slate-800 pt-1.5 flex justify-between font-extrabold text-sm text-slate-100">
                    <span>Итого к предоплате:</span>
                    <span className="text-emerald-400">
                      {product.price.toLocaleString()} {product.currency}
                    </span>
                  </div>
                  <div className="mt-2 rounded-xl bg-amber-500/10 border border-amber-500/30 p-2 text-[11px] font-bold text-amber-300 flex items-center gap-1.5">
                    <span>🔒 100% Предоплата заказа (Оплата при получении НЕ поддерживается)</span>
                  </div>
                </div>

                {/* Submit Order */}
                <button
                  onClick={handleCreateOrder}
                  disabled={isSubmitting}
                  className="w-full rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 py-3.5 text-xs font-extrabold text-white shadow-lg glow-cyan hover:opacity-95 transition-all flex items-center justify-center gap-2"
                >
                  <ShoppingBag className="w-4 h-4" />
                  {isSubmitting ? 'Оформление заказа...' : 'Оформить выкуп в ПВЗ'}
                </button>
              </div>
            )}

            {/* TAB 2: SELF ORDER (Secondary Flow) */}
            {activeTab === 'self_order' && (
              <div className="space-y-4 animate-in fade-in">
                <div className="p-3.5 rounded-2xl bg-amber-500/10 border border-amber-500/30 text-xs text-amber-200 space-y-2">
                  <div className="font-extrabold flex items-center gap-1.5 text-amber-300">
                    <ShieldCheck className="w-4 h-4 text-amber-400" />
                    Справка по самостоятельной покупке (НЕ через выкуп ПВЗ):
                  </div>
                  <ul className="text-[11px] space-y-1.5 text-slate-300 leading-relaxed list-disc pl-4">
                    <li>
                      <strong>1. Скопируйте адрес ПВЗ</strong> ниже и укажите его в качестве адреса доставки (Địa chỉ) на маркетплейсе.
                    </li>
                    <li>
                      <strong>2. Укажите ваше имя и ID получателя</strong> в поле «Имя получателя» (Tên người nhận) для точности идентификации.
                    </li>
                    <li>
                      <strong>📦 Условия хранения:</strong> Бесплатное хранение посылки в ПВЗ — 7 дней с момента прихода. Далее хранение и выдача осуществляются согласно правилам и тарифам компании.
                    </li>
                  </ul>
                </div>

                {/* Copyable Personal ID */}
                <div className="space-y-1">
                  <label className="text-[11px] font-semibold text-slate-400">1. Ваш персональный ID получателя (указать в имени):</label>
                  <div className="flex items-center justify-between rounded-xl bg-slate-950 border border-slate-800 p-2.5">
                    <span className="font-mono text-sm font-extrabold text-cyan-400">
                      {recipientName} ({personalShippingId})
                    </span>
                    <button
                      onClick={() => handleCopy(`${recipientName} (${personalShippingId})`, 'id')}
                      className="flex items-center gap-1 rounded-lg bg-cyan-500/20 border border-cyan-500/30 px-2.5 py-1 text-[11px] font-bold text-cyan-300 hover:bg-cyan-500/30"
                    >
                      {copiedField === 'id' ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                      {copiedField === 'id' ? 'Скопировано!' : 'Копировать'}
                    </button>
                  </div>
                </div>

                {/* Copyable Address */}
                <div className="space-y-1">
                  <label className="text-[11px] font-semibold text-slate-400">2. Точный адрес ПВЗ (для поля Adresse / Địa chỉ):</label>
                  <div className="rounded-xl bg-slate-950 border border-slate-800 p-3 space-y-2">
                    <p className="text-xs font-semibold text-slate-200 leading-relaxed">{currentPvz.address_vn}</p>
                    <div className="flex justify-between items-center border-t border-slate-800/80 pt-2">
                      <span className="text-[10px] text-slate-500">Телефон ПВЗ: {currentPvz.phone}</span>
                      <button
                        onClick={() => handleCopy(currentPvz.address_vn, 'address')}
                        className="flex items-center gap-1 rounded-lg bg-slate-800 px-2.5 py-1 text-[11px] font-bold text-slate-200 hover:bg-slate-700"
                      >
                        {copiedField === 'address' ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                        {copiedField === 'address' ? 'Скопировано!' : 'Скопировать адрес'}
                      </button>
                    </div>
                  </div>
                </div>

                {/* Direct link to market */}
                <a
                  href={product.product_url || 'https://shopee.vn'}
                  target="_blank"
                  rel="noreferrer"
                  className="w-full rounded-xl bg-slate-800 border border-slate-700 py-3 text-xs font-bold text-slate-100 hover:bg-slate-700 flex items-center justify-center gap-2"
                >
                  Перейти на маркетплейс ({product.platform.toUpperCase()}) <ExternalLink className="w-3.5 h-3.5 text-cyan-400" />
                </a>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};
