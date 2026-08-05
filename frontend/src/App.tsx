import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { HomeScreen } from './components/HomeScreen';
import { SearchScreen } from './components/SearchScreen';
import { ProductDetailScreen } from './components/ProductDetailScreen';
import { AlertsScreen } from './components/AlertsScreen';
import { PvzOrdersScreen } from './components/PvzOrdersScreen';

declare global {
  interface Window {
    Telegram?: {
      WebApp?: any;
    };
  }
}

export function App() {
  const [activeTab, setActiveTab] = useState('home');
  const [selectedProductId, setSelectedProductId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    if (window.Telegram?.WebApp) {
      window.Telegram.WebApp.ready();
      window.Telegram.WebApp.expand();
    }
  }, []);

  const handleSearchSubmit = (query: string) => {
    setSearchQuery(query);
    setActiveTab('search');
  };

  const handleSelectProduct = (productId: string) => {
    setSelectedProductId(productId);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 max-w-md mx-auto relative px-4 pt-3 font-sans">
      {selectedProductId ? (
        <ProductDetailScreen
          productId={selectedProductId}
          onBack={() => setSelectedProductId(null)}
        />
      ) : (
        <>
          {activeTab === 'home' && (
            <HomeScreen
              onSearchSubmit={handleSearchSubmit}
              onSelectProduct={handleSelectProduct}
            />
          )}
          {activeTab === 'search' && (
            <SearchScreen
              initialQuery={searchQuery || 'Sony WH-1000XM5'}
              onSelectProduct={handleSelectProduct}
            />
          )}
          {activeTab === 'pvz_orders' && (
            <PvzOrdersScreen onSelectProduct={handleSelectProduct} />
          )}
          {activeTab === 'alerts' && (
            <AlertsScreen onSelectProduct={handleSelectProduct} />
          )}
          {activeTab === 'favorites' && (
            <AlertsScreen onSelectProduct={handleSelectProduct} />
          )}
        </>
      )}

      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />
    </div>
  );
}

export default App;

