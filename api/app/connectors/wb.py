import httpx
from typing import List, Optional
from app.connectors.base import BaseMarketplaceConnector, StandardOffer
from app.config import settings

class WildberriesConnector(BaseMarketplaceConnector):
    SEARCH_URL = "https://search.wb.ru/exactmatch/ru/common/v4/search"

    async def search_products(self, query: str, limit: int = 20) -> List[StandardOffer]:
        offers = []
        try:
            params = {
                "appType": 1,
                "curr": "rub",
                "dest": -1257786,
                "query": query,
                "resultset": "catalog",
                "limit": limit
            }
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(self.SEARCH_URL, params=params)
                if res.status_code == 200:
                    data = res.json()
                    products = data.get("data", {}).get("products", [])
                    for item in products:
                        sku = str(item.get("id"))
                        price_u = item.get("sizes", [{}])[0].get("price", {}).get("total", 0) / 100
                        old_price_u = item.get("sizes", [{}])[0].get("price", {}).get("basic", 0) / 100
                        
                        image_url = f"https://basket-01.wbbasket.ru/vol{int(sku)//100000}/part{int(sku)//1000}/{sku}/images/c516x688/1.webp"
                        
                        offers.append(StandardOffer(
                            platform="wb",
                            external_sku=sku,
                            title=item.get("name", query),
                            brand=item.get("brand"),
                            price=price_u if price_u > 0 else float(item.get("salePriceU", 0)) / 100,
                            old_price=old_price_u if old_price_u > price_u else None,
                            currency="RUB",
                            product_url=f"https://www.wildberries.ru/catalog/{sku}/detail.aspx",
                            image_url=image_url,
                            in_stock=True,
                            rating=float(item.get("rating", 0)),
                            reviews_count=item.get("feedbacks", 0)
                        ))
        except Exception as e:
            print(f"Error in WB Search: {e}")
        return offers

    async def get_product_by_sku(self, sku: str) -> Optional[StandardOffer]:
        results = await self.search_products(query=sku, limit=1)
        return results[0] if results else None

wb_connector = WildberriesConnector()
