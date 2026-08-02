from fastapi import APIRouter, Depends, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, List
from app.db.session import get_db
from app.connectors.wb import wb_connector
from app.connectors.ozon import ozon_connector
from app.connectors.yandex import yandex_connector
from app.connectors.shopee import shopee_connector
from app.connectors.lazada import lazada_connector
from app.connectors.shein import shein_connector
from app.services.matcher import product_matcher
from app.models import MasterProduct, Offer

router = APIRouter(prefix="/search", tags=["Search"])

@router.get("")
async def search_products(
    q: str = Query(..., description="Search query string"),
    marketplace: Optional[str] = Query("all", description="shopee, lazada, shein, wb, ozon, yandex_market, all"),
    sort: Optional[str] = Query("relevance", description="price_asc, price_desc, relevance"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    # Fetch from connectors concurrently
    offers = []
    if marketplace in ["all", "shopee"]:
        offers.extend(await shopee_connector.search_products(q, limit=limit))
    if marketplace in ["all", "lazada"]:
        offers.extend(await lazada_connector.search_products(q, limit=limit))
    if marketplace in ["all", "shein"]:
        offers.extend(await shein_connector.search_products(q, limit=limit))
    if marketplace in ["all", "wb"]:
        offers.extend(await wb_connector.search_products(q, limit=limit))
    if marketplace in ["all", "ozon"]:
        offers.extend(await ozon_connector.search_products(q, limit=limit))
    if marketplace in ["all", "yandex_market"]:
        offers.extend(await yandex_connector.search_products(q, limit=limit))

    # Match offers to master products
    master_items = []
    for offer in offers[:limit]:
        master = await product_matcher.match_or_create_master_product(db, offer)
        master_items.append({
            "master_id": str(master.id),
            "title": master.title,
            "brand": master.brand,
            "main_image": master.main_image_url or offer.image_url,
            "price": offer.price,
            "old_price": offer.old_price,
            "platform": offer.platform,
            "url": offer.product_url,
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
