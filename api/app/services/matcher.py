import uuid
import re
from typing import List, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import MasterProduct, Offer
from app.connectors.base import StandardOffer
from app.services.qdrant_service import qdrant_service
from app.services.meili_service import meili_service

def clean_title(title: str) -> str:
    # Remove common promotional stop-words
    title = re.sub(r'(?i)\b(скидка|акция|распродажа|хит|бесплатная доставка|новинка)\b', '', title)
    return ' '.join(title.split()).lower()

def calculate_string_similarity(s1: str, s2: str) -> float:
    s1_clean = clean_title(s1)
    s2_clean = clean_title(s2)
    words1 = set(s1_clean.split())
    words2 = set(s2_clean.split())
    if not words1 or not words2:
        return 0.0
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    return len(intersection) / len(union)

class ProductMatcher:
    SIMILARITY_THRESHOLD = 0.75

    async def match_or_create_master_product(self, session: AsyncSession, offer_data: StandardOffer) -> MasterProduct:
        # Step 1: Check if offer with exact platform & SKU already exists
        existing_offer_stmt = select(Offer).where(
            Offer.platform == offer_data.platform,
            Offer.external_sku == offer_data.external_sku
        )
        res = await session.execute(existing_offer_stmt)
        existing_offer = res.scalars().first()

        if existing_offer and existing_offer.master_id:
            master = await session.get(MasterProduct, existing_offer.master_id)
            if master:
                # Update offer price
                existing_offer.current_price = offer_data.price
                existing_offer.old_price = offer_data.old_price
                await session.commit()
                return master

        # Step 2: Fuzzy / String Title match across existing MasterProducts
        stmt = select(MasterProduct).order_by(MasterProduct.created_at.desc()).limit(100)
        res = await session.execute(stmt)
        candidate_masters = res.scalars().all()

        best_master = None
        best_score = 0.0

        for candidate in candidate_masters:
            score = calculate_string_similarity(offer_data.title, candidate.title)
            if score > best_score:
                best_score = score
                best_master = candidate

        if best_master and best_score >= self.SIMILARITY_THRESHOLD:
            # Bind new offer to existing master product
            new_offer = Offer(
                master_id=best_master.id,
                platform=offer_data.platform,
                external_sku=offer_data.external_sku,
                title=offer_data.title,
                current_price=offer_data.price,
                old_price=offer_data.old_price,
                currency=offer_data.currency,
                product_url=offer_data.product_url,
                image_url=offer_data.image_url,
                in_stock=offer_data.in_stock,
                rating=offer_data.rating,
                reviews_count=offer_data.reviews_count
            )
            session.add(new_offer)
            await session.commit()
            return best_master

        # Step 3: Create new MasterProduct if no match meets threshold
        new_master = MasterProduct(
            id=uuid.uuid4(),
            title=offer_data.title,
            brand=offer_data.brand,
            main_image_url=offer_data.image_url
        )
        session.add(new_master)
        await session.flush()

        new_offer = Offer(
            master_id=new_master.id,
            platform=offer_data.platform,
            external_sku=offer_data.external_sku,
            title=offer_data.title,
            current_price=offer_data.price,
            old_price=offer_data.old_price,
            currency=offer_data.currency,
            product_url=offer_data.product_url,
            image_url=offer_data.image_url,
            in_stock=offer_data.in_stock,
            rating=offer_data.rating,
            reviews_count=offer_data.reviews_count
        )
        session.add(new_offer)
        await session.commit()

        # Update Meilisearch index asynchronously
        await meili_service.add_or_update_documents([{
            "id": str(new_master.id),
            "title": new_master.title,
            "brand": new_master.brand or "",
            "min_price": float(offer_data.price),
            "platforms": [offer_data.platform]
        }])

        return new_master

product_matcher = ProductMatcher()
