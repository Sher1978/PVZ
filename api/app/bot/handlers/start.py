from aiogram import Router, types
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from app.config import settings

router = Router()

@router.message(CommandStart())
async def command_start_handler(message: types.Message, command: CommandObject):
    start_param = command.args
    user_name = message.from_user.first_name if message.from_user else "друг"

    tma_url = "https://tma.smartsearch.app"
    if start_param and start_param.startswith("p_"):
        product_id = start_param.replace("p_", "")
        tma_url = f"https://tma.smartsearch.app/product/{product_id}"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 Открыть SmartSearch TMA",
                    web_app=WebAppInfo(url=tma_url)
                )
            ],
            [
                InlineKeyboardButton(text="🔔 Мои Алерты", callback_data="my_alerts"),
                InlineKeyboardButton(text="ℹ️ Помощь", callback_data="help_info")
            ]
        ]
    )

    welcome_text = (
        f"👋 Привет, {user_name}!\n\n"
        f"Я **SmartSearch Bot** — ваш умный помощник по поиску и сравнению цен "
        f"на Wildberries, Ozon, Яндекс.Маркет и AliExpress.\n\n"
        f"💡 **Что я умею:**\n"
        f"• Отправьте мне название товара или артикул для мгновенного поиска.\n"
        f"• Отправьте фото товара — я найду его по картинке.\n"
        f"• Пришлите ссылку на товар — я покажу, где он дешевле всего.\n\n"
        f"Нажмите кнопку ниже, чтобы запустить Mini App:"
    )

    await message.answer(welcome_text, reply_markup=keyboard, parse_mode="Markdown")
