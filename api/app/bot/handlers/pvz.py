from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from app.config import settings

router = Router()

PVZ_INFO_TEXT = (
    "📍 **ПВЗ SMARTSEARCH И СЛУЖБА ДОСТАВКИ ВО ВЬЕТНАМЕ** 🇻🇳\n\n"
    "Добро пожаловать в сервис доставки и выкупа товаров в Вьетнаме!\n\n"
    "🏢 **Пункты выдачи (ПВЗ):**\n"
    "• **Нячанг (Север / North Beach):** ул. Pham Van Dong (рядом с пляжем)\n"
    "• **Нячанг (Анвьен / An Vien):** ул. Tran Phu (район вилл)\n"
    "• **Дананг & Сайгон:** Партнерские хабы экспресс-выдачи\n\n"
    "🕒 **Часы работы:** Ежедневно с **9:00 до 23:00** без выходных.\n\n"
    "🛵 **Курьерская доставка «Прямо в руки»:**\n"
    "• Отправьте вашу геолокацию в чат бота — курьер доставит заказ в любой отель или кондоминиум.\n"
    "• Время доставки по Нячангу: от **15 до 45 минут**.\n\n"
    "📦 **Наши услуги:**\n"
    "1️⃣ **Выкуп с маркетплейсов:** Shopee, Lazada, Tiki, Shein, TikTok Shop, Kiki.\n"
    "2️⃣ **Прием личных посылок:** Организуем доставку из РФ и Китая.\n"
    "3️⃣ **Хранение в ПВЗ:** Бесплатное хранение ваших заказов до 14 дней.\n\n"
    "💡 **Используйте Mini App для оформления заказа или сравнения цен!**"
)

def get_pvz_keyboard():
    webapp_url = getattr(settings, "WEBAPP_URL", "https://smartsearch-tma.vercel.app").rstrip("/")
    support_username = getattr(settings, "SUPPORT_USERNAME", "pvz_support").lstrip("@")
    
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🚀 Открыть SmartSearch Mini App", web_app=WebAppInfo(url=webapp_url))
            ],
            [
                InlineKeyboardButton(text="💬 Написать оператору ПВЗ", url=f"https://t.me/{support_username}"),
                InlineKeyboardButton(text="🔨 Спец Аукцион", callback_data="refresh_auction_menu")
            ]
        ]
    )

@router.message(Command("pvz"))
@router.message(F.text == "📍 НАШ ПВЗ")
@router.message(F.text == "📍 Наш ПВЗ")
async def pvz_info_handler(message: types.Message):
    await message.answer(PVZ_INFO_TEXT, reply_markup=get_pvz_keyboard(), parse_mode="Markdown")
