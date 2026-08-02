from aiogram import Bot, Dispatcher
from app.config import settings
from app.bot.handlers import start, search

bot = Bot(token=settings.BOT_TOKEN) if settings.BOT_TOKEN else None
dp = Dispatcher()

dp.include_router(start.router)
dp.include_router(search.router)
