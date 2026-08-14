from fastapi import APIRouter, Depends, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, List
from app.db.session import get_db
from app.connectors.shopee import shopee_connector
from app.connectors.lazada import lazada_connector
from app.connectors.tiki import tiki_connector
from app.connectors.shein import shein_connector
from app.connectors.kiki import kiki_connector
from app.connectors.tiktok import tiktok_connector
from app.services.accesstrade import generate_affiliate_link
from app.services.matcher import product_matcher
from app.models import MasterProduct, Offer

from app.services.url_parser import resolve_search_query, is_url_input, detect_url_platform
from app.config import settings

router = APIRouter(prefix="/search", tags=["Search"])

@router.get("")
async def search_products(
    q: str = Query(..., description="Search query string"),
    marketplace: Optional[str] = Query("all", description="shopee, lazada, tiki, shein, kiki, tiktok, all"),
    sort: Optional[str] = Query("relevance", description="price_asc, price_desc, relevance"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    # Direct URL Referral Conversion Handler
    if is_url_input(q):
        target_url = q.strip() if (q.strip().startswith("http://") or q.strip().startswith("https://")) else f"https://{q.strip()}"
        platform = detect_url_platform(target_url)
        extracted_title = await resolve_search_query(q)

        if platform:
            tracked_url = await generate_affiliate_link(platform=platform, product_url=target_url, sub1="direct_link")
            # Verify if referral code was attached (tracked_url differs or token configured)
            if tracked_url != target_url:
                return {
                    "is_url_convert": True,
                    "success": True,
                    "platform": platform,
                    "original_url": target_url,
                    "referral_url": tracked_url,
                    "title": extracted_title or "Товар по ссылке",
                    "items": []
                }
            else:
                return {
                    "is_url_convert": True,
                    "success": False,
                    "error": f"Не удалось сгенерировать реферальную ссылку для {platform.upper()}. Реферальная кампания или токен ACCESSTRADE не настроены.",
                    "platform": platform,
                    "original_url": target_url,
                    "items": []
                }
        else:
            return {
                "is_url_convert": True,
                "success": False,
                "error": "Ссылка принадлежит нерасшифрованному или неподдерживаемому маркетплейсу.",
                "original_url": target_url,
                "items": []
            }

    # Resolve product URL to keywords if input is a URL
    search_keywords = await resolve_search_query(q)

    # Fetch from Vietnam marketplaces concurrently
    offers = []
    if marketplace in ["all", "shopee"]:
        offers.extend(await shopee_connector.search_products(search_keywords, limit=limit))
    if marketplace in ["all", "lazada"]:
        offers.extend(await lazada_connector.search_products(search_keywords, limit=limit))
    if marketplace in ["all", "tiki"]:
        offers.extend(await tiki_connector.search_products(search_keywords, limit=limit))
    if marketplace in ["all", "shein"]:
        offers.extend(await shein_connector.search_products(search_keywords, limit=limit))
    if marketplace in ["all", "kiki"]:
        offers.extend(await kiki_connector.search_products(search_keywords, limit=limit))
    if marketplace in ["all", "tiktok"]:
        offers.extend(await tiktok_connector.search_products(search_keywords, limit=limit))

    # Match offers to master products
    master_items = []
    for offer in offers[:limit]:
        try:
            master = await product_matcher.match_or_create_master_product(db, offer)
            master_id = str(master.id)
            title = master.title
            brand = master.brand
            image = master.main_image_url or offer.image_url
        except Exception as e:
            print(f"DB matching fallback: {e}")
            master_id = f"mst_{offer.external_sku}"
            title = offer.title
            brand = offer.brand
            image = offer.image_url

        # Generate ACCESSTRADE affiliate link for supported platforms
        affiliate_platforms = {"lazada", "shopee", "kiki", "tiktok"}
        tracked_url = offer.product_url
        if offer.platform in affiliate_platforms:
            tracked_url = await generate_affiliate_link(
                platform=offer.platform,
                product_url=offer.product_url,
                sub1=master_id,
            )

        master_items.append({
            "master_id": master_id,
            "title": title,
            "brand": brand,
            "main_image": image,
            "images": getattr(offer, "images", None) or ([image] if image else []),
            "price": offer.price,
            "old_price": offer.old_price,
            "platform": offer.platform,
            "currency": offer.currency,
            "url": tracked_url,
            "rating": offer.rating,
            "reviews_count": offer.reviews_count
        })

    if sort == "price_asc":
        master_items.sort(key=lambda x: x["price"])
    elif sort == "price_desc":
        master_items.sort(key=lambda x: x["price"], reverse=True)

    return {
        "total": len(master_items),
        "page": page,
        "limit": limit,
        "items": master_items
    }

@router.post("/by-image")
async def search_by_image(file: UploadFile = File(...)):
    # Mock response for vision CLIP matching SLA
    return {
        "match_score": 0.94,
        "items": [
            {
                "master_id": "mst_vision_123",
                "title": "Наушники Sony WH-1000XM5 Black (Распознано по фото)",
                "min_price": 28990.00,
                "platforms": ["ozon", "wb"]
            }
        ]
    }
