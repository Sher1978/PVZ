import React, { useState } from 'react';
import { HelpCircle, ChevronDown, ChevronUp, MessageSquare, Truck, Package, ShieldCheck, MapPin, ExternalLink, PhoneCall } from 'lucide-react';

interface HelpModalProps {
  onClose: () => void;
}

interface FaqItem {
  question: string;
  answer: string;
  category: 'pvz' | 'order' | 'search';
}

const FAQ_ITEMS: FaqItem[] = [
  {
    category: 'pvz',
    question: 'Как работает выкуп товара с доставкой в ПВЗ?',
    answer: 'Мы берем на себя весь процесс: от выкупа товара на маркетплейсе (Shopee, Lazada, Tiki) до его приемки и проверки в нашем ПВЗ в Нячанге, Дананге или Сайгоне. Вам достаточно выбрать товар, нажать «Выкупить через ПВЗ» и получить ПИН-код выдачи.'
  },
  {
    category: 'pvz',
    question: 'Где находятся пункты выдачи (ПВЗ) во Вьетнаме?',
    answer: 'Наши главные ПВЗ работают в Нячанге (Pham Van Dong / Tran Phu), Дананге (Hai Chau) и Хошимине / Сайгоне (Ben Thanh). Точный адрес и рабочее время можно выбрать при оформлении заказа.'
  },
  {
    category: 'order',
    question: 'Могу ли я сам оформить заказ на адрес ПВЗ?',
    answer: 'Да! В окне выкупа выберите вкладку «2. Свой заказ в ПВЗ». Скопируйте наш адрес и укажите ваш персональный ID в поле имени получателя на Shopee/Lazada. Посылка прибудет на наш склад для вас.'
  },
  {
    category: 'order',
    question: 'Сколько хранится посылка в ПВЗ и какая стоимость?',
    answer: 'Бесплатное хранение составляет 7 дней с момента поступления на пункт выдачи. Выдача посылок при заказе через наш выкуп — БЕСПЛАТНО.'
  },
  {
    category: 'search',
    question: 'Как искать товар по ссылке с сайта?',
    answer: 'Вставьте скопированную ссылку на товар из приложения Shopee, Lazada, Tiki или веб-сайта в поисковую строку. SmartSearch автоматически распознает заголовок и найдет лучшие цены.'
  },
  {
    category: 'search',
    question: 'Как работает поиск по фото?',
    answer: 'Нажмите на иконку камеры 📷 на главном экране или в поиске, загрузите скриншот или фото любого товара. AI-движок найдет аналогичные предложения на вьетнамских маркетплейсах.'
  }
];

export const HelpModal: React.FC<HelpModalProps> = ({ onClose }) => {
  const [openFaqIndex, setOpenFaqIndex] = useState<number | null>(0);
  const [activeCategory, setActiveCategory] = useState<'all' | 'pvz' | 'order' | 'search'>('all');

  const toggleFaq = (index: number) => {
    setOpenFaqIndex(openFaqIndex === index ? null : index);
    if (window.Telegram?.WebApp?.HapticFeedback) {
      window.Telegram.WebApp.HapticFeedback.impactOccurred('light');
    }
  };

  const filteredFaqs = activeCategory === 'all' 
    ? FAQ_ITEMS 
    : FAQ_ITEMS.filter(item => item.category === activeCategory);

  const handleOpenSupport = () => {
    if (window.Telegram?.WebApp?.HapticFeedback) {
      window.Telegram.WebApp.HapticFeedback.notificationOccurred('success');
    }
    window.open('https://t.me/smartsearch_support', '_blank');
  };

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/80 backdrop-blur-md p-3 animate-in fade-in">
      <div className="w-full max-w-lg rounded-3xl bg-slate-900 border border-slate-800 p-5 space-y-4 shadow-2xl max-h-[85vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-cyan-500/20 border border-cyan-500/40 text-cyan-400">
              <HelpCircle className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-extrabold text-slate-100">Центр Помощи SmartSearch</h3>
              <p className="text-[11px] text-slate-400">Справка и поддержка во Вьетнаме 🇻🇳</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-slate-800 text-slate-400 hover:text-white flex items-center justify-center font-bold text-sm"
          >
            ✕
          </button>
        </div>

        {/* Quick Contact Banner */}
        <div className="glass-panel rounded-2xl p-4 border border-cyan-500/30 bg-gradient-to-r from-cyan-950/40 via-slate-900 to-slate-900 flex items-center justify-between gap-3">
          <div className="space-y-1 min-w-0">
            <div className="flex items-center gap-1.5 text-xs font-bold text-slate-100">
              <MessageSquare className="w-4 h-4 text-cyan-400" /> Служба поддержки 24/7
            </div>
            <p className="text-[11px] text-slate-400">
              Возник вопрос по выкупу или посылке? Операторы на связи в Telegram!
            </p>
          </div>
          <button
            onClick={handleOpenSupport}
            className="rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white px-3.5 py-2 text-xs font-extrabold shadow-md flex items-center gap-1.5 whitespace-nowrap transition-all"
          >
            <span>Написать</span> <ExternalLink className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Category Filters */}
        <div className="flex gap-1.5 overflow-x-auto pb-1 text-xs scrollbar-none">
          <button
            onClick={() => setActiveCategory('all')}
            className={`px-3 py-1.5 rounded-xl font-medium transition-all ${
              activeCategory === 'all' 
                ? 'bg-cyan-500 text-white font-bold' 
                : 'bg-slate-950 text-slate-400 border border-slate-800'
            }`}
          >
            Все вопросы
          </button>
          <button
            onClick={() => setActiveCategory('pvz')}
            className={`px-3 py-1.5 rounded-xl font-medium transition-all ${
              activeCategory === 'pvz' 
                ? 'bg-cyan-500 text-white font-bold' 
                : 'bg-slate-950 text-slate-400 border border-slate-800'
            }`}
          >
            ПВЗ и Доставка 🇻🇳
          </button>
          <button
            onClick={() => setActiveCategory('order')}
            className={`px-3 py-1.5 rounded-xl font-medium transition-all ${
              activeCategory === 'order' 
                ? 'bg-cyan-500 text-white font-bold' 
                : 'bg-slate-950 text-slate-400 border border-slate-800'
            }`}
          >
            Заказы и Выкуп
          </button>
          <button
            onClick={() => setActiveCategory('search')}
            className={`px-3 py-1.5 rounded-xl font-medium transition-all ${
              activeCategory === 'search' 
                ? 'bg-cyan-500 text-white font-bold' 
                : 'bg-slate-950 text-slate-400 border border-slate-800'
            }`}
          >
            Поиск и Фото
          </button>
        </div>

        {/* Accordion List */}
        <div className="space-y-2">
          {filteredFaqs.map((faq, idx) => {
            const isOpen = openFaqIndex === idx;
            return (
              <div
                key={idx}
                className="rounded-2xl bg-slate-950/80 border border-slate-800/80 overflow-hidden transition-all"
              >
                <button
                  onClick={() => toggleFaq(idx)}
                  className="w-full p-3.5 text-left text-xs font-bold text-slate-200 flex items-center justify-between gap-2 hover:text-cyan-400 transition-colors"
                >
                  <span className="flex-1">{faq.question}</span>
                  {isOpen ? (
                    <ChevronUp className="w-4 h-4 text-cyan-400 shrink-0" />
                  ) : (
                    <ChevronDown className="w-4 h-4 text-slate-500 shrink-0" />
                  )}
                </button>
                {isOpen && (
                  <div className="px-3.5 pb-3.5 pt-1 text-xs text-slate-400 leading-relaxed border-t border-slate-900 animate-in fade-in">
                    {faq.answer}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Close Button */}
        <button
          onClick={onClose}
          className="w-full rounded-xl bg-slate-800 border border-slate-700 py-3 text-xs font-bold text-slate-200 hover:bg-slate-700 transition-all mt-2"
        >
          Закрыть справку
        </button>
      </div>
    </div>
  );
};
