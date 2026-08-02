from aiogram import Bot, Dispatcher
from app.config import settings
from app.bot.handlers import start, search

try:
    bot = Bot(token=settings.BOT_TOKEN) if settings.BOT_TOKEN else None
except Exception:
    bot = None
dp = Dispatcher()

dp.include_router(start.router)
dp.include_router(search.router)
