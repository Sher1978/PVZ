import React, { useState, useEffect } from 'react';
import { User, Phone, MapPin, Building, Save, Loader2, CheckCircle2, ShieldCheck, Truck, Bell, HelpCircle } from 'lucide-react';
import { HelpModal } from './HelpModal';

interface ProfileScreenProps {
  onNavigateDelivery?: () => void;
  onNavigateAlerts?: () => void;
  onOpenHelp?: () => void;
}

const API_BASE = (import.meta as any).env?.VITE_API_URL || '';

export const ProfileScreen: React.FC<ProfileScreenProps> = ({ onNavigateDelivery, onNavigateAlerts, onOpenHelp }) => {
  const tgUser = window.Telegram?.WebApp?.initDataUnsafe?.user;
  const telegramId = tgUser?.id || 123456789;
  const initialName = tgUser ? `${tgUser.first_name || ''} ${tgUser.last_name || ''}`.trim() || 'Пользователь' : 'Пользователь ПВЗ';
  const [showHelpModal, setShowHelpModal] = useState(false);

  const [firstName, setFirstName] = useState(initialName);
  const [phoneNumber, setPhoneNumber] = useState('');
  const [deliveryAddress, setDeliveryAddress] = useState('');
  const [city, setCity] = useState('Нячанг');
  const [preferredPvz, setPreferredPvz] = useState('Нячанг (Север)');
  const [notes, setNotes] = useState('');

  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  useEffect(() => {
    const fetchProfile = async () => {
      setIsLoading(true);
      try {
        const res = await fetch(`${API_BASE}/api/v1/user/profile?telegram_id=${telegramId}`);
        if (res.ok) {
          const data = await res.json();
          if (data.first_name) setFirstName(data.first_name);
          if (data.phone_number) setPhoneNumber(data.phone_number);
          if (data.delivery_address) setDeliveryAddress(data.delivery_address);
          if (data.city) setCity(data.city);
          if (data.preferred_pvz) setPreferredPvz(data.preferred_pvz);
          if (data.notes) setNotes(data.notes);
        }
      } catch (e) {
        console.error('Failed to load profile:', e);
      } finally {
        setIsLoading(false);
      }
    };

    fetchProfile();
  }, [telegramId]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setSavedSuccess(false);

    if (window.Telegram?.WebApp?.HapticFeedback) {
      window.Telegram.WebApp.HapticFeedback.notificationOccurred('success');
    }

    try {
      const res = await fetch(`${API_BASE}/api/v1/user/profile`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          telegram_id: telegramId,
          first_name: firstName,
          phone_number: phoneNumber,
          delivery_address: deliveryAddress,
          city: city,
          preferred_pvz: preferredPvz,
          notes: notes,
        })
      });

      if (res.ok) {
        setSavedSuccess(true);
        setTimeout(() => setSavedSuccess(false), 3000);
      }
    } catch (e) {
      console.error('Failed to save profile:', e);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-4 pb-28 pt-2">
      {/* Profile Banner */}
      <div className="glass-panel rounded-2xl p-5 border border-slate-800 bg-gradient-to-b from-cyan-950/30 to-slate-900 flex items-center gap-4">
        <div className="w-14 h-14 rounded-2xl bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center text-cyan-400 font-extrabold text-xl shadow-lg glow-cyan">
          {tgUser?.photo_url ? (
            <img src={tgUser.photo_url} alt="avatar" className="w-full h-full rounded-2xl object-cover" />
          ) : (
            <User className="w-7 h-7" />
          )}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h1 className="text-base font-extrabold text-slate-100 truncate">{firstName}</h1>
            <span className="flex items-center gap-1 rounded bg-emerald-500/20 px-1.5 py-0.5 text-[9px] font-bold text-emerald-400">
              <ShieldCheck className="w-3 h-3" /> Вьетнам 🇻🇳
            </span>
          </div>
          <p className="text-xs text-slate-400">ID Telegram: `{telegramId}`</p>
        </div>
      </div>

      {/* Success Notification Alert */}
      {savedSuccess && (
        <div className="rounded-xl bg-emerald-500/20 border border-emerald-500/40 p-3 text-xs font-bold text-emerald-400 flex items-center gap-2 animate-in fade-in">
          <CheckCircle2 className="w-4 h-4" />
          Данные профиля успешно сохранены и синхронизированы с Ботом!
        </div>
      )}

      {/* Profile Form */}
      <form onSubmit={handleSave} className="glass-panel rounded-2xl p-5 border border-slate-800 space-y-4">
        <h2 className="text-sm font-bold text-slate-100 flex items-center gap-2">
          <User className="w-4 h-4 text-cyan-400" /> Настройка личных данных и адреса
        </h2>

        {isLoading ? (
          <div className="py-8 text-center text-slate-400 text-xs flex items-center justify-center gap-2">
            <Loader2 className="w-4 h-4 animate-spin text-cyan-400" /> Загрузка данных профиля...
          </div>
        ) : (
          <div className="space-y-3">
            {/* Phone input */}
            <div>
              <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5 mb-1.5">
                <Phone className="w-3.5 h-3.5 text-cyan-400" /> Контактный телефон (WhatsApp / Telegram)
              </label>
              <input
                type="text"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                placeholder="+84 123 456 789"
                className="w-full rounded-xl bg-slate-900 border border-slate-800 py-3 px-3.5 text-sm text-slate-100 focus:border-cyan-500 focus:outline-none"
              />
            </div>

            {/* City select */}
            <div>
              <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5 mb-1.5">
                <MapPin className="w-3.5 h-3.5 text-cyan-400" /> Город пребывания во Вьетнаме
              </label>
              <select
                value={city}
                onChange={(e) => setCity(e.target.value)}
                className="w-full rounded-xl bg-slate-900 border border-slate-800 py-3 px-3.5 text-sm text-slate-100 focus:border-cyan-500 focus:outline-none"
              >
                <option value="Нячанг">Нячанг (Nha Trang)</option>
                <option value="Дананг">Дананг (Da Nang)</option>
                <option value="Сайгон">Сайгон / Хошимин (Ho Chi Minh)</option>
                <option value="Фукуок">Остров Фукуок (Phu Quoc)</option>
                <option value="Другой">Другой город</option>
              </select>
            </div>

            {/* Delivery Address */}
            <div>
              <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5 mb-1.5">
                <MapPin className="w-3.5 h-3.5 text-emerald-400" /> Точный адрес доставки курьером
              </label>
              <textarea
                value={deliveryAddress}
                onChange={(e) => setDeliveryAddress(e.target.value)}
                rows={2}
                placeholder="Улица, отель / кондоминиум, номер комнаты (например: Nha Trang, Pham Van Dong 12, room 1402)"
                className="w-full rounded-xl bg-slate-900 border border-slate-800 py-2.5 px-3.5 text-sm text-slate-100 focus:border-cyan-500 focus:outline-none"
              />
            </div>

            {/* Preferred PVZ */}
            <div>
              <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5 mb-1.5">
                <Building className="w-3.5 h-3.5 text-cyan-400" /> Предпочитаемый ПВЗ / Способ получения
              </label>
              <select
                value={preferredPvz}
                onChange={(e) => setPreferredPvz(e.target.value)}
                className="w-full rounded-xl bg-slate-900 border border-slate-800 py-3 px-3.5 text-sm text-slate-100 focus:border-cyan-500 focus:outline-none"
              >
                <option value="Нячанг (Север)">ПВЗ Нячанг — Север (Pham Van Dong)</option>
                <option value="Нячанг (Анвьен)">ПВЗ Нячанг — Анвьен (Tran Phu)</option>
                <option value="Курьерская доставка">Доставка курьером прямо на локацию 🛵</option>
              </select>
            </div>

            {/* Notes */}
            <div>
              <label className="text-xs font-semibold text-slate-400 mb-1 block">
                Пожелания к доставке / Ориентир
              </label>
              <input
                type="text"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Оставить на ресепшн, перед приездом позвонить и т.д."
                className="w-full rounded-xl bg-slate-900 border border-slate-800 py-2.5 px-3.5 text-xs text-slate-100 focus:border-cyan-500 focus:outline-none"
              />
            </div>

            {/* Save Button */}
            <button
              type="submit"
              disabled={isSaving}
              className="w-full rounded-xl bg-gradient-to-r from-cyan-500 to-teal-600 py-3.5 text-xs font-extrabold text-white shadow-lg glow-cyan flex items-center justify-center gap-2 hover:opacity-95 transition-all mt-2"
            >
              {isSaving ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" /> Сохранение...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4" /> Сохранить изменения
                </>
              )}
            </button>
          </div>
        )}
      </form>

      {/* Quick Action Links */}
      <div className="space-y-2">
        {onNavigateDelivery && (
          <button
            onClick={onNavigateDelivery}
            className="w-full rounded-2xl bg-slate-900 border border-slate-800 p-4 text-xs font-bold text-slate-300 hover:text-white flex items-center justify-between transition-all"
          >
            <div className="flex items-center gap-2.5">
              <Truck className="w-4 h-4 text-cyan-400" />
              <span>Мои доставки и статус посылок</span>
            </div>
            <span className="text-cyan-400 font-extrabold text-xs">Перейти →</span>
          </button>
        )}

        {onNavigateAlerts && (
          <button
            onClick={onNavigateAlerts}
            className="w-full rounded-2xl bg-slate-900 border border-slate-800 p-4 text-xs font-bold text-slate-300 hover:text-white flex items-center justify-between transition-all"
          >
            <div className="flex items-center gap-2.5">
              <Bell className="w-4 h-4 text-amber-400" />
              <span>Мои Алерты (Подписки на цены)</span>
            </div>
            <span className="text-amber-400 font-extrabold text-xs">Открыть →</span>
          </button>
        )}

        <button
          onClick={() => {
            if (onOpenHelp) onOpenHelp();
            else setShowHelpModal(true);
          }}
          className="w-full rounded-2xl bg-slate-900 border border-slate-800 p-4 text-xs font-bold text-slate-300 hover:text-white flex items-center justify-between transition-all"
        >
          <div className="flex items-center gap-2.5">
            <HelpCircle className="w-4 h-4 text-emerald-400" />
            <span>Помощь и Поддержка 💬</span>
          </div>
          <span className="text-emerald-400 font-extrabold text-xs">Справка / Чат →</span>
        </button>
      </div>

      {showHelpModal && (
        <HelpModal onClose={() => setShowHelpModal(false)} />
      )}
    </div>
  );
};
