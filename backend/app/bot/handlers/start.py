from aiogram import Router, types, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from app.config import settings

router = Router()

def get_welcome_text_and_keyboard(user_name: str, start_param: str | None = None):
    base_url = getattr(settings, "WEBAPP_URL", "https://tma.smartsearch.app").rstrip("/")
    tma_url = base_url
    if start_param and start_param.startswith("p_"):
        product_id = start_param.replace("p_", "")
        tma_url = f"{base_url}/product/{product_id}"

    support_username = getattr(settings, "SUPPORT_USERNAME", "pvz_support").lstrip("@")
    support_url = f"https://t.me/{support_username}"

    welcome_text = (
        f"👋 **Привет, {user_name}! Добро пожаловать в сервис ПВЗ Нячанг!**\n\n"
        f"🔍 **Ищите товары по лучшей цене и сравнивайте цены в нашем приложении!**\n"
        f"В нашем Mini App вы можете быстро найти любой товар и мгновенно сравнить стоимость "
        f"на всех вьетнамских площадках (**Shopee, Lazada, Tiki** и др.), чтобы заказать по самой выгодной цене.\n\n"
        f"⭐ **Наши главные преимущества:**\n\n"
        f"1️⃣ **Русская поддержка 💬**\n"
        f"Никакого языкового барьера. Наша русскоязычная команда всегда на связи и поможет решить любой вопрос!\n\n"
        f"2️⃣ **Доставка прямо в руки в удобное время 🛵**\n"
        f"• Доставляем ежедневно в любое время с **9:00 до 23:00**.\n"
        f"• **Зона работы:** Нячанг, Северный район (North Beach) и Анвьен (An Vien).\n"
        f"• **Доставка на локацию:** Просто поделитесь геолокацией в Telegram, и курьер привезет заказ прямо к вам!\n\n"
        f"3️⃣ **Сравнение цен на маркетплейсах 📊**\n"
        f"Выбирайте самые низкие цены и экономьте на каждой покупке с вьетнамских платформ.\n\n"
        f"💡 **Нажмите кнопку ниже, чтобы запустить поиск товаров или написать менеджеру:**"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 Открыть SmartSearch TMA",
                    web_app=WebAppInfo(url=tma_url)
                )
            ],
            [
                InlineKeyboardButton(text="💬 Мгновенная поддержка", url=support_url),
                InlineKeyboardButton(text="🔨 Спец Аукцион", callback_data="refresh_auction_menu")
            ],
            [
                InlineKeyboardButton(text="ℹ️ Инструкция и Сервис", callback_data="help_info")
            ]
        ]
    )
    return welcome_text, keyboard

@router.message(CommandStart())
async def command_start_handler(message: types.Message, command: CommandObject):
    user_name = message.from_user.first_name if message.from_user else "друг"
    welcome_text, keyboard = get_welcome_text_and_keyboard(user_name, command.args)
    await message.answer(welcome_text, reply_markup=keyboard, parse_mode="Markdown")

@router.callback_query(F.data == "help_info")
async def help_info_callback_handler(callback: types.CallbackQuery):
    user_name = callback.from_user.first_name if callback.from_user else "друг"
    welcome_text, keyboard = get_welcome_text_and_keyboard(user_name)
    try:
        await callback.message.edit_text(welcome_text, reply_markup=keyboard, parse_mode="Markdown")
        await callback.answer()
    except Exception:
        await callback.message.answer(welcome_text, reply_markup=keyboard, parse_mode="Markdown")
        await callback.answer()
