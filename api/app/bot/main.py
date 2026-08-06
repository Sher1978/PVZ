from aiogram import Bot, Dispatcher
from aiogram.types import MenuButtonWebApp, WebAppInfo
from app.config import settings
from app.bot.handlers import start, search

try:
    bot = Bot(token=settings.BOT_TOKEN) if settings.BOT_TOKEN else None
except Exception:
    bot = None
dp = Dispatcher()

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

dp.startup.register(on_startup)
dp.include_router(start.router)
dp.include_router(search.router)
