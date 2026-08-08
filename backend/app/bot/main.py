import asyncio
from datetime import datetime, timezone
from sqlalchemy import select
from aiogram import Bot, Dispatcher
from aiogram.types import MenuButtonWebApp, WebAppInfo

from app.config import settings
from app.db.session import AsyncSessionLocal
from app.models.auction import Auction
from app.services.auction_service import finish_auction
from app.bot.handlers import start, search, auction, admin_auction, admin_roles

try:
    bot = Bot(token=settings.BOT_TOKEN) if settings.BOT_TOKEN else None
except Exception:
    bot = None

dp = Dispatcher()

async def check_expired_auctions_loop(bot: Bot):
    while True:
        try:
            await asyncio.sleep(15)
            if not bot:
                continue
            async with AsyncSessionLocal() as session:
                now = datetime.now(timezone.utc)
                stmt = select(Auction).where(
                    Auction.status == "active",
                    Auction.end_time <= now
                )
                res = await session.execute(stmt)
                expired_auctions = res.scalars().all()
                for auc in expired_auctions:
                    await finish_auction(bot, session, auc.id)
        except Exception as e:
            print(f"Error in auction expiration loop: {e}")

async def on_startup(bot: Bot):
    webapp_url = getattr(settings, "WEBAPP_URL", "https://tma.smartsearch.app")
    try:
        await bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(
                text="🚀 Открыть SmartSearch",
                web_app=WebAppInfo(url=webapp_url)
            )
        )
    except Exception as e:
        print(f"Failed to set chat menu button: {e}")

    # Launch background auction expiration monitor loop
    asyncio.create_task(check_expired_auctions_loop(bot))

dp.startup.register(on_startup)
dp.include_router(start.router)
dp.include_router(search.router)
dp.include_router(auction.router)
dp.include_router(admin_auction.router)
dp.include_router(admin_roles.router)
