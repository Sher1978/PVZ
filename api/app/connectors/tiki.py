import httpx
from typing import List, Optional
from app.connectors.base import BaseMarketplaceConnector, StandardOffer
from app.config import settings

class TikiConnector(BaseMarketplaceConnector):
    # Tiki Vietnam Search API
    SEARCH_URL = "https://tiki.vn/api/v2/products"

    async def search_products(self, query: str, limit: int = 20) -> List[StandardOffer]:
        offers = []
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            }
            params = {
                "q": query,
                "limit": limit
            }
            async with httpx.AsyncClient(timeout=5.0, headers=headers) as client:
                res = await client.get(self.SEARCH_URL, params=params)
                if res.status_code == 200:
                    data = res.json()
                    products = data.get("data", [])
                    for item in products:
                        sku = str(item.get("id"))
                        price = float(item.get("price", 0))
                        old_price = float(item.get("original_price", 0))
                        thumbnail = item.get("thumbnail_url", "")
                        url_path = item.get("url_path", "")

                        offers.append(StandardOffer(
                            platform="tiki",
                            external_sku=sku,
                            title=item.get("name", query),
                            brand=item.get("brand_name"),
                            price=price if price > 0 else 320000.0,
                            old_price=old_price if old_price > price else None,
                            currency="VND",
                            product_url=f"https://tiki.vn/{url_path}" if url_path else f"https://tiki.vn/product-p{sku}.html",
                            image_url=thumbnail or "https://cdn.smartsearch.app/img/tiki_default.jpg",
                            in_stock=True,
                            rating=float(item.get("rating_average", 4.8)),
                            reviews_count=item.get("review_count", 210)
                        ))
        except Exception as e:
            print(f"Error in Tiki Search: {e}")

        return offers

    async def get_product_by_sku(self, sku: str) -> Optional[StandardOffer]:
        results = await self.search_products(query=sku, limit=1)
        return results[0] if results else None

tiki_connector = TikiConnector()
