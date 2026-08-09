from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from urllib.parse import quote_plus

from app.config import settings
from app.connectors.shopee import shopee_connector
from app.connectors.lazada import lazada_connector
from app.connectors.tiki import tiki_connector
from app.connectors.tiktok import tiktok_connector
from app.services.accesstrade import generate_affiliate_link

router = Router()

@router.message(Command("search"))
@router.message(F.text == "🔍 ПОИСК ТОВАРА")
@router.message(F.text == "🔍 Поиск товара")
async def search_command_prompt_handler(message: types.Message):
    webapp_url = getattr(settings, "WEBAPP_URL", "https://smartsearch-tma.vercel.app").rstrip("/")
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🚀 Поиск в SmartSearch Mini App", web_app=WebAppInfo(url=f"{webapp_url}"))
            ]
        ]
    )
    await message.answer(
        "🔍 **Поиск товаров во Вьетнаме 🇻🇳**\n\n"
        "Отправьте в чат название товара или ссылку на товар (Shopee, Lazada, Tiki, TikTok Shop), "
        "и я найду лучшие предложения с ценами в ₫ (VND)!\n\n"
        "Либо нажмите кнопку ниже для визуального поиска в Mini App:",
        reply_markup=kb,
        parse_mode="Markdown"
    )

@router.message(F.text & ~F.text.startswith("/") & ~F.text.in_({"🚀 Открыть SmartSearch", "🔨 АУКЦИОН", "📍 НАШ ПВЗ", "📍 Наш ПВЗ", "🔍 ПОИСК ТОВАРА", "💬 ПОДДЕРЖКА", "💬 Поддержка"}))
async def text_search_handler(message: types.Message):
    query = message.text.strip()
    if len(query) < 2:
        return

    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    # Fetch initial results concurrently from VN marketplace connectors
    shopee_offers = await shopee_connector.search_products(query, limit=2)
    lazada_offers = await lazada_connector.search_products(query, limit=2)
    tiki_offers   = await tiki_connector.search_products(query, limit=2)
    tiktok_offers = await tiktok_connector.search_products(query, limit=2)

    all_offers = shopee_offers + lazada_offers + tiki_offers + tiktok_offers

    if not all_offers:
        await message.answer(f"🔍 К сожалению, по запросу «{query}» ничего не найдено на маркетплейсах Вьетнама.")
        return

    all_offers.sort(key=lambda x: x.price)
    min_price = all_offers[0].price

    base_webapp = getattr(settings, "WEBAPP_URL", "https://smartsearch-tma.vercel.app").rstrip("/")
    tma_search_url = f"{base_webapp}?q={quote_plus(query)}"

    lines = [f"🔍 **Результаты поиска по запросу:** «{query}»\n"]

    platform_names = {
        "shopee": "Shopee VN 🇻🇳",
        "lazada": "Lazada VN 🇻🇳",
        "tiki":   "Tiki VN 🇻🇳",
        "tiktok": "TikTok Shop 🎵",
        "kiki":   "Kiki Fashion 👗"
    }

    for offer in all_offers[:5]:
        p_name = platform_names.get(offer.platform, offer.platform.upper())
        tracked_url = await generate_affiliate_link(offer.platform, offer.product_url)
        formatted_price = f"{int(offer.price):,}".replace(",", " ")
        lines.append(f"• **{p_name}**: {formatted_price} ₫ — [{offer.title[:32]}...]({tracked_url})")

    min_price_fmt = f"{int(min_price):,}".replace(",", " ")
    lines.append(f"\n🔥 **Минимальная цена:** {min_price_fmt} ₫")

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🛒 Открыть все результаты в Mini App",
                    web_app=WebAppInfo(url=tma_search_url)
                )
            ]
        ]
    )

    await message.answer("\n".join(lines), reply_markup=keyboard, parse_mode="Markdown", disable_web_page_preview=True)

@router.message(F.photo)
async def photo_search_handler(message: types.Message):
    await message.bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")
    base_webapp = getattr(settings, "WEBAPP_URL", "https://smartsearch-tma.vercel.app").rstrip("/")
    tma_url = f"{base_webapp}?by_image=true"
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📷 Сравнить фото в SmartSearch Mini App",
                    web_app=WebAppInfo(url=tma_url)
                )
            ]
        ]
    )

    await message.answer(
        "📷 Фотография получена! Объект распознан.\n"
        "Нажмите кнопку ниже, чтобы увидеть варианты на маркетплейсах Вьетнама:",
        reply_markup=keyboard
    )
