from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db
from app.models.user import User

router = APIRouter(prefix="/user", tags=["User Profile"])

class UserProfileRequest(BaseModel):
    telegram_id: int
    first_name: Optional[str] = None
    phone_number: Optional[str] = None
    delivery_address: Optional[str] = None
    city: Optional[str] = "Нячанг"
    preferred_pvz: Optional[str] = "Нячанг (Север)"
    notes: Optional[str] = None

class UserProfileResponse(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: str
    phone_number: Optional[str] = None
    delivery_address: Optional[str] = None
    city: str = "Нячанг"
    preferred_pvz: str = "Нячанг (Север)"
    notes: Optional[str] = None
    is_admin: bool = False
    is_auction_subscribed: bool = True

@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    telegram_id: int = Query(..., description="Telegram User ID"),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(User).where(User.telegram_id == telegram_id)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()

    if not user:
        # Create default record for new user
        user = User(
            telegram_id=telegram_id,
            first_name=f"User {telegram_id}",
            city="Нячанг",
            preferred_pvz="Нячанг (Север)"
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return UserProfileResponse(
        telegram_id=user.telegram_id,
        username=user.username,
        first_name=user.first_name,
        phone_number=user.phone_number,
        delivery_address=user.delivery_address,
        city=user.city or "Нячанг",
        preferred_pvz=user.preferred_pvz or "Нячанг (Север)",
        notes=user.notes,
        is_admin=user.is_admin,
        is_auction_subscribed=user.is_auction_subscribed
    )

@router.put("/profile", response_model=UserProfileResponse)
async def update_user_profile(
    req: UserProfileRequest,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(User).where(User.telegram_id == req.telegram_id)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()

    if not user:
        user = User(
            telegram_id=req.telegram_id,
            first_name=req.first_name or f"User {req.telegram_id}"
        )
        db.add(user)

    if req.first_name:
        user.first_name = req.first_name
    if req.phone_number is not None:
        user.phone_number = req.phone_number
    if req.delivery_address is not None:
        user.delivery_address = req.delivery_address
    if req.city is not None:
        user.city = req.city
    if req.preferred_pvz is not None:
        user.preferred_pvz = req.preferred_pvz
    if req.notes is not None:
        user.notes = req.notes

    await db.commit()
    await db.refresh(user)

    return UserProfileResponse(
        telegram_id=user.telegram_id,
        username=user.username,
        first_name=user.first_name,
        phone_number=user.phone_number,
        delivery_address=user.delivery_address,
        city=user.city or "Нячанг",
        preferred_pvz=user.preferred_pvz or "Нячанг (Север)",
        notes=user.notes,
        is_admin=user.is_admin,
        is_auction_subscribed=user.is_auction_subscribed
    )
