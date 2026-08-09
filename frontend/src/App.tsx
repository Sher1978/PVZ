import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { HomeScreen } from './components/HomeScreen';
import { SearchScreen } from './components/SearchScreen';
import { ProductDetailScreen } from './components/ProductDetailScreen';
import { AlertsScreen } from './components/AlertsScreen';
import { PvzOrdersScreen } from './components/PvzOrdersScreen';
import { ProfileScreen } from './components/ProfileScreen';

declare global {
  interface Window {
    Telegram?: {
      WebApp?: any;
    };
  }
}

export function App() {
  const [activeTab, setActiveTab] = useState('home');
  const [selectedProduct, setSelectedProduct] = useState<any | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    if (window.Telegram?.WebApp) {
      window.Telegram.WebApp.ready();
      window.Telegram.WebApp.expand();
    }

    const urlParams = new URLSearchParams(window.location.search);
    const tabParam = urlParams.get('tab');
    if (tabParam && ['home', 'search', 'pvz_orders', 'profile', 'alerts'].includes(tabParam)) {
      setActiveTab(tabParam);
    }
  }, []);

  const handleSearchSubmit = (query: string) => {
    setSearchQuery(query);
    setActiveTab('search');
  };

  const handleSelectProduct = (product: any) => {
    if (typeof product === 'string') {
      setSelectedProduct({ id: product, title: product });
    } else {
      setSelectedProduct(product);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 max-w-md mx-auto relative px-4 pt-3 font-sans">
      {selectedProduct && (
        <ProductDetailScreen
          productId={selectedProduct.id}
          productItem={selectedProduct}
          onBack={() => setSelectedProduct(null)}
        />
      )}

      <div className={selectedProduct ? 'hidden' : 'block'}>
        {activeTab === 'home' && (
          <HomeScreen
            onSearchSubmit={handleSearchSubmit}
            onSelectProduct={handleSelectProduct}
          />
        )}
        <div className={activeTab === 'search' ? 'block' : 'hidden'}>
          <SearchScreen
            initialQuery={searchQuery || 'Sony WH-1000XM5'}
            onSelectProduct={handleSelectProduct}
          />
        </div>
        {activeTab === 'pvz_orders' && (
          <PvzOrdersScreen onSelectProduct={handleSelectProduct} />
        )}
        {activeTab === 'profile' && (
          <ProfileScreen onNavigateDelivery={() => setActiveTab('pvz_orders')} />
        )}
        {activeTab === 'alerts' && (
          <AlertsScreen onSelectProduct={handleSelectProduct} />
        )}
      </div>

      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />
    </div>
  );
}

export default App;
