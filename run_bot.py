import asyncio
import logging
import os
import sys

# Append backend directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from app.config import settings
from app.bot.main import bot, dp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

async def main():
    if not bot:
        logging.error("❌ BOT_TOKEN is missing or invalid in .env! Cannot start bot.")
        return

    try:
        me = await bot.get_me()
        logging.info(f"🚀 Telegram Bot started successfully: @{me.username} (ID: {me.id})")
        
        # Remove any existing webhook so long polling works
        await bot.delete_webhook(drop_pending_updates=False)
        logging.info("⚡ Webhook cleared. Launching Long Polling listener...")

        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"❌ Error starting bot: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())
