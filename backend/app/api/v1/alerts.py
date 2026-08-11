from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
import uuid
from app.db.session import get_db
from app.models import PriceAlert, Offer, MasterProduct
from app.bot.main import bot

router = APIRouter(prefix="/alerts", tags=["Price Alerts"])

class CreateAlertRequest(BaseModel):
    master_id: str
    target_price: float
    notify_on_any_drop: bool = False

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_price_alert(req: CreateAlertRequest, db: AsyncSession = Depends(get_db)):
    try:
        master_uuid = uuid.UUID(req.master_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid master_id UUID format")

    alert = PriceAlert(
        user_id=1,
        master_id=master_uuid,
        target_price=req.target_price,
        notify_on_any_drop=req.notify_on_any_drop
    )
    db.add(alert)
    await db.commit()
    await db.refresh(alert)

    return {
        "status": "success",
        "alert_id": str(alert.id),
        "target_price": float(alert.target_price)
    }

@router.get("")
async def get_user_alerts(db: AsyncSession = Depends(get_db)):
    stmt = select(PriceAlert).where(PriceAlert.is_active == True)
    res = await db.execute(stmt)
    alerts = res.scalars().all()
    return [
        {
            "alert_id": str(a.id),
            "master_id": str(a.master_id),
            "target_price": float(a.target_price),
            "created_at": a.created_at
        }
        for a in alerts
    ]

@router.delete("/{alert_id}")
async def delete_user_alert(alert_id: str, db: AsyncSession = Depends(get_db)):
    try:
        alert_uuid = uuid.UUID(alert_id)
    except ValueError:
        # If it's a string id (e.g. alert_1) or mock id, return success status
        return {"status": "success", "alert_id": alert_id}

    stmt = select(PriceAlert).where(PriceAlert.id == alert_uuid)
    res = await db.execute(stmt)
    alert = res.scalars().first()
    if alert:
        alert.is_active = False
        await db.commit()

    return {"status": "success", "alert_id": alert_id}

@router.get("/check-cron")
async def check_alerts_cron(db: AsyncSession = Depends(get_db)):
    """
    Invoked periodically by Vercel Cron (every 15 minutes) to monitor price drops
    """
    stmt = select(PriceAlert).where(PriceAlert.is_active == True)
    res = await db.execute(stmt)
    active_alerts = res.scalars().all()

    checked_count = 0
    notifications_sent = 0

    for alert in active_alerts:
        checked_count += 1
        # Fetch lowest offer price for this master product
        offer_stmt = select(Offer).where(Offer.master_id == alert.master_id).order_by(Offer.current_price.asc()).limit(1)
        offer_res = await db.execute(offer_stmt)
        lowest_offer = offer_res.scalars().first()

        if lowest_offer and lowest_offer.current_price <= alert.target_price:
            # Trigger Telegram bot notification if bot is configured
            if bot:
                try:
                    await bot.send_message(
                        chat_id=alert.user_id,
                        text=f"📉 **Скидка на {lowest_offer.title}!**\nНовая цена: {lowest_offer.current_price:,.0f} ₽ на {lowest_offer.platform.upper()}"
                    )
                    notifications_sent += 1
                except Exception as e:
                    print(f"Error sending bot cron alert: {e}")

    return {
        "status": "cron completed successfully",
        "alerts_checked": checked_count,
        "notifications_sent": notifications_sent
    }
