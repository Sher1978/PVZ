from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.db.session import AsyncSessionLocal
from app.models.orders import PvzOrderModel

router = Router()

STATUS_EMOJI = {
    "pending": "📦 В обработке",
    "purchased": "💳 Выкуплен",
    "in_transit": "🚚 В пути на ПВЗ",
    "ready": "🏢 Готов к выдаче в ПВЗ",
    "completed": "✅ Завершен",
    "cancelled": "❌ Отменен"
}

@router.message(Command("delivery"))
@router.message(F.text == "🚚 ДОСТАВКИ")
@router.message(F.text == "🚚 Доставки")
async def delivery_menu_handler(message: types.Message):
    user_id = str(message.from_user.id)
    webapp_url = getattr(settings, "WEBAPP_URL", "https://smartsearch-tma.vercel.app").rstrip("/")
    tma_delivery_url = f"{webapp_url}?tab=pvz_orders"

    async with AsyncSessionLocal() as session:
        stmt = select(PvzOrderModel).where(PvzOrderModel.user_telegram_id == user_id).order_by(PvzOrderModel.created_at.desc()).limit(10)
        res = await session.execute(stmt)
        orders = res.scalars().all()

    if not orders:
        text = (
            "🚚 **РАЗДЕЛ ДОСТАВКИ И ТРЕКИНГА** 🇻🇳\n\n"
            "У вас пока нет активных заказов или посылок.\n\n"
            "💡 **Вы можете:**\n"
            "1. Выкупить любой товар с Shopee, Lazada, Tiki, TikTok Shop через наш Mini App.\n"
            "2. Зарегистрировать самостоятельный заказ на адрес нашего ПВЗ.\n"
            "3. Заказать доставку курьером прямо на вашу локацию!"
        )
    else:
        text_lines = ["🚚 **ВАШИ ДОСТАВКИ И ПОСЫЛКИ** 🇻🇳\n"]
        for order in orders:
            st = STATUS_EMOJI.get(order.status, order.status)
            price_fmt = f"{int(order.price):,}".replace(",", " ") if order.price else "0"
            text_lines.append(
                f"• **{order.product_title[:30]}**\n"
                f"  Статус: {st}\n"
                f"  ПВЗ: {order.pvz_name}\n"
                f"  Код выдачи: `{order.pickup_code}` | Сумма: {price_fmt} {order.currency}\n"
            )
        text = "\n".join(text_lines)

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🚀 Открыть все заказы в Mini App", web_app=WebAppInfo(url=tma_delivery_url))
            ],
            [
                InlineKeyboardButton(text="📍 Информация о ПВЗ", callback_data="pvz_info_cb"),
                InlineKeyboardButton(text="💬 Написать оператору", url=f"https://t.me/{getattr(settings, 'SUPPORT_USERNAME', 'pvz_support').lstrip('@')}")
            ]
        ]
    )

    await message.answer(text, reply_markup=kb, parse_mode="Markdown")
