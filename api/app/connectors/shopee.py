import httpx
from typing import List, Optional
from app.connectors.base import BaseMarketplaceConnector, StandardOffer
from app.config import settings

class ShopeeConnector(BaseMarketplaceConnector):
    # Shopee Vietnam Public Search Endpoint
    SEARCH_URL = "https://shopee.vn/api/v4/search/search_items"

    async def search_products(self, query: str, limit: int = 20) -> List[StandardOffer]:
        offers = []
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Referer": f"https://shopee.vn/search?keyword={query}"
            }
            params = {
                "by": "relevance",
                "keyword": query,
                "limit": limit,
                "newest": 0,
                "order": "desc",
                "page_type": "search",
                "scenario": "PAGE_GLOBAL_SEARCH",
                "version": 2
            }
            async with httpx.AsyncClient(timeout=5.0, headers=headers) as client:
                res = await client.get(self.SEARCH_URL, params=params)
                if res.status_code == 200:
                    data = res.json()
                    items = data.get("items", []) or data.get("data", {}).get("items", [])
                    for entry in items:
                        item = entry.get("item_basic", entry)
                        itemid = str(item.get("itemid"))
                        shopid = str(item.get("shopid"))
                        raw_price = item.get("price", 0) / 100000  # Shopee raw price scale factor
                        raw_old_price = item.get("price_before_discount", 0) / 100000
                        image_hash = item.get("image", "")
                        images_hashes = item.get("images", []) or ([image_hash] if image_hash else [])
                        images_urls = [f"https://down-vn.img.susercontent.com/file/{h}" for h in images_hashes if h]

                        image_url = images_urls[0] if images_urls else "https://cdn.smartsearch.app/img/shopee_default.jpg"
                        product_url = f"https://shopee.vn/product/{shopid}/{itemid}"

                        offers.append(StandardOffer(
                            platform="shopee",
                            external_sku=f"{shopid}_{itemid}",
                            title=item.get("name", query),
                            brand=item.get("brand"),
                            price=raw_price if raw_price > 0 else 150000.0,
                            old_price=raw_old_price if raw_old_price > raw_price else None,
                            currency="VND",
                            product_url=product_url,
                            image_url=image_url,
                            images=images_urls if images_urls else [image_url],
                            in_stock=True,
                            rating=float(item.get("item_rating", {}).get("rating_star", 4.8)),
                            reviews_count=item.get("historical_sold", 120)
                        ))
        except Exception as e:
            print(f"Error in Shopee Search: {e}")

        return offers

    async def get_product_by_sku(self, sku: str) -> Optional[StandardOffer]:
        results = await self.search_products(query=sku, limit=1)
        return results[0] if results else None

shopee_connector = ShopeeConnector()
