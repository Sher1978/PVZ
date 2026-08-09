import React from 'react';
import { Search, Bell, Home, Truck, User } from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab }) => {
  const navItems = [
    { id: 'home', label: 'Главная', icon: Home },
    { id: 'search', label: 'Поиск', icon: Search },
    { id: 'pvz_orders', label: 'Доставки', icon: Truck },
    { id: 'profile', label: 'Профиль', icon: User },
    { id: 'alerts', label: 'Алерты', icon: Bell },
  ];

  const handleTabClick = (id: string) => {
    if (window.Telegram?.WebApp?.HapticFeedback) {
      window.Telegram.WebApp.HapticFeedback.impactOccurred('light');
    }
    setActiveTab(id);
  };

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 glass-panel border-t border-slate-800/80 px-4 py-2">
      <div className="max-w-md mx-auto flex justify-between items-center">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => handleTabClick(item.id)}
              className={`flex flex-col items-center gap-1 transition-all duration-200 ${
                isActive
                  ? 'text-cyan-400 scale-105 font-semibold'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <div
                className={`p-1.5 rounded-xl transition-all ${
                  isActive ? 'bg-cyan-500/10 border border-cyan-500/30' : ''
                }`}
              >
                <Icon className="w-5 h-5" />
              </div>
              <span className="text-[11px]">{item.label}</span>
            </button>
          );
        })}
      </div>
    </nav>
  );
};
