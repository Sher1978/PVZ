from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from app.connectors.wb import wb_connector
from app.connectors.ozon import ozon_connector
from app.connectors.yandex import yandex_connector

router = Router()

@router.message(F.text & ~F.text.startswith("/"))
async def text_search_handler(message: types.Message):
    query = message.text.strip()
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    # Fetch initial results concurrently
    wb_results = await wb_connector.search_products(query, limit=2)
    ozon_results = await ozon_connector.search_products(query, limit=2)
    yandex_results = await yandex_connector.search_products(query, limit=2)

    all_offers = wb_results + ozon_results + yandex_results

    if not all_offers:
        await message.answer(f"🔍 К сожалению, по запросу «{query}» ничего не найдено.")
        return

    min_price = min(o.price for o in all_offers)
    tma_search_url = f"https://tma.smartsearch.app/search?q={query}"

    lines = [f"🔍 **Результаты поиска по запросу:** «{query}»\n"]
    for offer in all_offers[:4]:
        lines.append(f"• **{offer.platform.upper()}**: {offer.price:,.0f} ₽ — [{offer.title[:30]}...]({offer.product_url})")

    lines.append(f"\n🔥 **Минимальная цена:** {min_price:,.0f} ₽")

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🛒 Открыть все результаты в TMA",
                    web_app=WebAppInfo(url=tma_search_url)
                )
            ]
        ]
    )

    await message.answer("\n".join(lines), reply_markup=keyboard, parse_mode="Markdown", disable_web_page_preview=True)

@router.message(F.photo)
async def photo_search_handler(message: types.Message):
    await message.bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")
    tma_url = "https://tma.smartsearch.app/search?by_image=true"
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📷 Сравнить фото в SmartSearch TMA",
                    web_app=WebAppInfo(url=tma_url)
                )
            ]
        ]
    )

    await message.answer(
        "📷 Фотография получена! Мы распознали объект на картинке.\n"
        "Нажмите кнопку ниже, чтобы увидеть похожие товары на всех маркетплейсах:",
        reply_markup=keyboard
    )
