from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class StandardOffer(BaseModel):
    platform: str
    external_sku: str
    title: str
    brand: Optional[str] = None
    price: float
    old_price: Optional[float] = None
    currency: str = "RUB"
    product_url: str
    image_url: Optional[str] = None
    in_stock: bool = True
    rating: Optional[float] = None
    reviews_count: int = 0

class BaseMarketplaceConnector(ABC):
    @abstractmethod
    async def search_products(self, query: str, limit: int = 20) -> List[StandardOffer]:
        pass

    @abstractmethod
    async def get_product_by_sku(self, sku: str) -> Optional[StandardOffer]:
        pass
