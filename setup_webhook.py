import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from aiogram import Bot

async def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        print("❌ BOT_TOKEN not found in .env")
        return

    domain = os.getenv("WEBAPP_URL", "https://smartsearch-tma.vercel.app").rstrip("/")
    webhook_url = f"{domain}/api/v1/bot/webhook"

    bot = Bot(token=token)
    try:
        me = await bot.get_me()
        print(f"Bot: @{me.username}")
        print(f"Setting Webhook to: {webhook_url}")
        
        res = await bot.set_webhook(url=webhook_url, drop_pending_updates=False)
        if res:
            print("SUCCESS: Webhook set successfully!")
        else:
            print("ERROR: Failed to set webhook.")
            
        info = await bot.get_webhook_info()
        print(f"Webhook Info: URL='{info.url}', Pending Updates={info.pending_update_count}")
    except Exception as e:
        print(f"Error setting webhook: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
