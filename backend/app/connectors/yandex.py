import httpx
from typing import List, Optional
from app.connectors.base import BaseMarketplaceConnector, StandardOffer

class YandexMarketConnector(BaseMarketplaceConnector):
    async def search_products(self, query: str, limit: int = 20) -> List[StandardOffer]:
        mock_sku = f"ym_{hash(query) % 1000000}"
        return [
            StandardOffer(
                platform="yandex_market",
                external_sku=mock_sku,
                title=f"{query} (Яндекс Маркет Доставка)",
                brand="Original",
                price=31200.00 if "sony" in query.lower() else 1300.00,
                old_price=34000.00 if "sony" in query.lower() else 1600.00,
                currency="RUB",
                product_url=f"https://market.yandex.ru/product--{query.replace(' ', '-')}/{mock_sku}",
                image_url="https://cdn.smartsearch.app/img/yandex_default.jpg",
                in_stock=True,
                rating=4.8,
                reviews_count=140
            )
        ]

    async def get_product_by_sku(self, sku: str) -> Optional[StandardOffer]:
        results = await self.search_products(query=sku, limit=1)
        return results[0] if results else None

yandex_connector = YandexMarketConnector()
