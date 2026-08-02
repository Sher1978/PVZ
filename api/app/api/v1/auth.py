from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_db
from app.auth.telegram_auth import verify_telegram_init_data
from app.config import settings
from app.models.user import User
import json

router = APIRouter(prefix="/auth", tags=["Auth"])

class TelegramLoginRequest(BaseModel):
    init_data: str

class UserSchema(BaseModel):
    telegram_id: int
    first_name: str
    username: str | None = None
    is_premium: bool = False

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserSchema

@router.post("/telegram-login", response_model=AuthResponse)
async def telegram_login(req: TelegramLoginRequest, db: AsyncSession = Depends(get_db)):
    if settings.BOT_TOKEN:
        parsed_data = verify_telegram_init_data(req.init_data, settings.BOT_TOKEN)
        user_raw = json.loads(parsed_data.get("user", "{}"))
    else:
        # Mock payload for dev mode if BOT_TOKEN not configured
        user_raw = {"id": 12345678, "first_name": "Developer", "username": "dev_user"}

    tg_id = user_raw.get("id")
    first_name = user_raw.get("first_name", "User")
    username = user_raw.get("username")

    stmt = select(User).where(User.telegram_id == tg_id)
    res = await db.execute(stmt)
    user = res.scalars().first()

    if not user:
        user = User(telegram_id=tg_id, first_name=first_name, username=username)
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return AuthResponse(
        access_token=f"mock_jwt_token_for_{tg_id}",
        token_type="bearer",
        user=UserSchema(
            telegram_id=user.telegram_id,
            first_name=user.first_name,
            username=user.username,
            is_premium=user.is_premium
        )
    )
