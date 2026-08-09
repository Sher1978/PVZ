import asyncio
from datetime import datetime, timezone
from sqlalchemy import select
from aiogram import Bot, Dispatcher
from aiogram.types import MenuButtonWebApp, WebAppInfo, BotCommand

from app.config import settings
from app.db.session import AsyncSessionLocal
from app.models.auction import Auction
from app.services.auction_service import finish_auction
from app.bot.handlers import start, search, auction, pvz, profile, delivery, admin_auction, admin_roles

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
    webapp_url = getattr(settings, "WEBAPP_URL", "https://smartsearch-tma.vercel.app").rstrip("/")

    # Register Bot Menu Commands
    try:
        commands = [
            BotCommand(command="start", description="🚀 Главное меню и поиск"),
            BotCommand(command="search", description="🔍 Поиск товаров во Вьетнаме (VND ₫)"),
            BotCommand(command="auction", description="🔨 Раздел «Спец Аукцион»"),
            BotCommand(command="delivery", description="🚚 Мои доставки и трекинг посылок"),
            BotCommand(command="pvz", description="📍 Информация о ПВЗ и Доставка"),
            BotCommand(command="profile", description="👤 Личный профиль (Адрес, Телефон, ПВЗ)"),
            BotCommand(command="help", description="💬 Поддержка и инструкции"),
            BotCommand(command="admin_auction", description="👑 Панель управления аукционами (Админ)"),
        ]
        await bot.set_my_commands(commands)
    except Exception as e:
        print(f"Failed to set bot commands: {e}")

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
dp.include_router(pvz.router)
dp.include_router(profile.router)
dp.include_router(delivery.router)
dp.include_router(admin_auction.router)
dp.include_router(admin_roles.router)


