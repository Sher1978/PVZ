from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo,
    ReplyKeyboardMarkup, KeyboardButton
)
from app.config import settings

router = Router()

def get_main_reply_keyboard():
    webapp_url = getattr(settings, "WEBAPP_URL", "https://smartsearch-tma.vercel.app").rstrip("/")
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🚀 Открыть SmartSearch", web_app=WebAppInfo(url=webapp_url))
            ],
            [
                KeyboardButton(text="🔨 АУКЦИОН"),
                KeyboardButton(text="🚚 ДОСТАВКИ")
            ],
            [
                KeyboardButton(text="👤 ПРОФИЛЬ"),
                KeyboardButton(text="📍 НАШ ПВЗ")
            ],
            [
                KeyboardButton(text="🔍 ПОИСК ТОВАРА"),
                KeyboardButton(text="💬 ПОДДЕРЖКА")
            ]
        ],
        resize_keyboard=True
    )


def get_welcome_text_and_keyboard(user_name: str, start_param: str | None = None):
    base_url = getattr(settings, "WEBAPP_URL", "https://smartsearch-tma.vercel.app").rstrip("/")
    tma_url = base_url
    if start_param and start_param.startswith("p_"):
        product_id = start_param.replace("p_", "")
        tma_url = f"{base_url}/product/{product_id}"

    support_username = getattr(settings, "SUPPORT_USERNAME", "pvz_support").lstrip("@")
    support_url = f"https://t.me/{support_username}"

    welcome_text = (
        f"👋 **Привет, {user_name}! Добро пожаловать в SmartSearch TMA & ПВЗ Вьетнам!** 🇻🇳\n\n"
        f"🔍 **Умный помощник для поиска товаров и выкупа со всех маркетплейсов Вьетнама!**\n"
        f"В нашем сервисе вы можете быстро найти любой товар, сравнить стоимость "
        f"на площадках (**Shopee, Lazada, Tiki, TikTok Shop, Shein, Kiki**) и заказать с доставкой в наш ПВЗ.\n\n"
        f"🔥 **Наши суперсилы:**\n"
        f"1️⃣ **Сравнение цен в ₫ (VND) 📊**\n"
        f"Показываем минимальные цены и лучшие предложения со всех маркетплейсов Вьетнама.\n\n"
        f"2️⃣ **Спец Аукционы 🔨**\n"
        f"Эксклюзивные товары с торгов по ценам ниже рынка с мгновенным выкупом.\n\n"
        f"3️⃣ **Русская поддержка и доставка 🛵**\n"
        f"• Доставляем курьером в Нячанге, Дананге и Сайгоне ежедневно с **9:00 до 23:00**.\n"
        f"• Выдаем посылки в комфортном ПВЗ в Нячанге (Север и Анвьен).\n\n"
        f"💡 **Нажмите «🚀 Открыть SmartSearch» в меню или ниже, чтобы начать!**"
    )

    inline_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 Открыть SmartSearch TMA",
                    web_app=WebAppInfo(url=tma_url)
                )
            ],
            [
                InlineKeyboardButton(text="🔨 Спец Аукцион", callback_data="refresh_auction_menu"),
                InlineKeyboardButton(text="📍 Наш ПВЗ", callback_data="pvz_info_cb")
            ],
            [
                InlineKeyboardButton(text="💬 Мгновенная поддержка", url=support_url),
                InlineKeyboardButton(text="ℹ️ Справка и Команды", callback_data="help_info")
            ]
        ]
    )
    return welcome_text, inline_keyboard

@router.message(CommandStart())
async def command_start_handler(message: types.Message, command: CommandObject):
    user_name = message.from_user.first_name if message.from_user else "друг"
    welcome_text, keyboard = get_welcome_text_and_keyboard(user_name, command.args)
    reply_kb = get_main_reply_keyboard()
    await message.answer(welcome_text, reply_markup=reply_kb, parse_mode="Markdown")
    await message.answer("👇 Пользуйтесь интерактивным меню ниже для быстрой навигации:", reply_markup=keyboard)

@router.message(Command("help"))
@router.message(F.text == "💬 ПОДДЕРЖКА")
@router.message(F.text == "💬 Поддержка")
async def help_command_handler(message: types.Message):
    support_username = getattr(settings, "SUPPORT_USERNAME", "pvz_support").lstrip("@")
    support_url = f"https://t.me/{support_username}"
    webapp_url = getattr(settings, "WEBAPP_URL", "https://smartsearch-tma.vercel.app").rstrip("/")

    text = (
        "💬 **СЛУЖБА ПОДДЕРЖКИ И КОМАНДЫ БОТА**\n\n"
        "Операторы русской поддержки на связи ежедневно с **9:00 до 23:00**.\n\n"
        "📌 **Доступные команды:**\n"
        "• `/start` — Запуск и главное меню\n"
        "• `/search` — Поиск товаров во Вьетнаме\n"
        "• `/auction` — Раздел спец аукционов\n"
        "• `/pvz` — Информация о пунктах выдачи и доставке\n"
        "• `/help` — Связь с поддержкой\n\n"
        "💡 **Вопросы по выкупу, доставке или оплате? Напишите нашему оператору!**"
    )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💬 Написать оператору", url=support_url)],
            [InlineKeyboardButton(text="🚀 Открыть Mini App", web_app=WebAppInfo(url=webapp_url))]
        ]
    )
    await message.answer(text, reply_markup=kb, parse_mode="Markdown")

@router.callback_query(F.data == "pvz_info_cb")
async def pvz_info_callback_handler(callback: types.CallbackQuery):
    from app.bot.handlers.pvz import PVZ_INFO_TEXT, get_pvz_keyboard
    await callback.message.answer(PVZ_INFO_TEXT, reply_markup=get_pvz_keyboard(), parse_mode="Markdown")
    await callback.answer()

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
