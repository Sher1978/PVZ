from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, WebAppInfo
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.db.session import AsyncSessionLocal
from app.models.user import User

router = Router()

class EditProfileState(StatesGroup):
    phone = State()
    address = State()
    city = State()

def get_profile_keyboard(user: User):
    webapp_url = getattr(settings, "WEBAPP_URL", "https://smartsearch-tma.vercel.app").rstrip("/")
    tma_profile_url = f"{webapp_url}?tab=profile"

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📱 Изменить телефон", callback_data="edit_profile_phone"),
                InlineKeyboardButton(text="📍 Изменить адрес", callback_data="edit_profile_address")
            ],
            [
                InlineKeyboardButton(text="🏙️ Сменить город", callback_data="edit_profile_city_select"),
                InlineKeyboardButton(text="🏢 Сменить ПВЗ", callback_data="edit_profile_pvz_select")
            ],
            [
                InlineKeyboardButton(text="🚀 Открыть Профиль в Mini App", web_app=WebAppInfo(url=tma_profile_url))
            ]
        ]
    )

def format_profile_text(user: User) -> str:
    phone = user.phone_number or "❌ Не указан"
    addr = user.delivery_address or "❌ Не указан"
    city = user.city or "Нячанг 🇻🇳"
    pvz = user.preferred_pvz or "Нячанг (Север)"

    return (
        f"👤 **ВАШ ПРОФИЛЬ ПВЗ SMARTSEARCH** 🇻🇳\n\n"
        f"👤 **Имя:** {user.first_name}\n"
        f"📱 **Телефон:** `{phone}`\n"
        f"🏙️ **Город:** {city}\n"
        f"📍 **Адрес доставки:** {addr}\n"
        f"🏢 **Выбранный ПВЗ:** {pvz}\n\n"
        f"💡 *Данные профиля автоматически подставляются при оформлении заказов и синхронизируются с Mini App!*"
    )

@router.message(Command("profile"))
@router.message(F.text == "👤 ПРОФИЛЬ")
@router.message(F.text == "👤 Профиль")
@router.callback_query(F.data == "user_profile_menu")
async def profile_menu_handler(event: types.Message | types.CallbackQuery):
    user_id = event.from_user.id
    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.telegram_id == user_id)
        res = await session.execute(stmt)
        user = res.scalar_one_or_none()

        if not user:
            user = User(
                telegram_id=user_id,
                username=event.from_user.username,
                first_name=event.from_user.first_name or "Пользователь",
                city="Нячанг",
                preferred_pvz="Нячанг (Север)"
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)

    text = format_profile_text(user)
    kb = get_profile_keyboard(user)

    if isinstance(event, types.CallbackQuery):
        try:
            await event.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
        except Exception:
            await event.message.answer(text, reply_markup=kb, parse_mode="Markdown")
        await event.answer()
    else:
        await event.answer(text, reply_markup=kb, parse_mode="Markdown")

@router.callback_query(F.data == "edit_profile_phone")
async def edit_phone_prompt(callback: types.CallbackQuery, state: FSMContext):
    contact_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Поделиться контактом Telegram", request_contact=True)],
            [KeyboardButton(text="❌ Отмена")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await state.set_state(EditProfileState.phone)
    await callback.message.answer(
        "📱 **Изменение телефона**\n\n"
        "Отправьте ваш номер телефона текстом (например: `+84123456789`) или нажмите кнопку **«📱 Поделиться контактом»** ниже:",
        reply_markup=contact_kb,
        parse_mode="Markdown"
    )
    await callback.answer()

@router.message(EditProfileState.phone, F.contact)
async def process_contact(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number
    user_id = message.from_user.id

    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.telegram_id == user_id)
        res = await session.execute(stmt)
        user = res.scalar_one_or_none()
        if user:
            user.phone_number = phone
            await session.commit()

    await state.clear()
    from app.bot.handlers.start import get_main_reply_keyboard
    await message.answer(f"✅ Телефон `{phone}` успешно сохранен в профиле!", reply_markup=get_main_reply_keyboard(), parse_mode="Markdown")

@router.message(EditProfileState.phone, F.text)
async def process_phone_text(message: types.Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        from app.bot.handlers.start import get_main_reply_keyboard
        await message.answer("❌ Изменение телефона отменено.", reply_markup=get_main_reply_keyboard())
        return

    phone = message.text.strip()
    user_id = message.from_user.id

    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.telegram_id == user_id)
        res = await session.execute(stmt)
        user = res.scalar_one_or_none()
        if user:
            user.phone_number = phone
            await session.commit()

    await state.clear()
    from app.bot.handlers.start import get_main_reply_keyboard
    await message.answer(f"✅ Телефон `{phone}` сохранен!", reply_markup=get_main_reply_keyboard(), parse_mode="Markdown")

@router.callback_query(F.data == "edit_profile_address")
async def edit_address_prompt(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(EditProfileState.address)
    await callback.message.answer(
        "📍 **Изменение адреса доставки во Вьетнаме**\n\n"
        "Введите ваш полный адрес (город, район, улица, отель / кондоминиум, номер комнаты):\n\n"
        "*(Например: Nha Trang, Pham Van Dong 12, Muong Thanh Hotel, room 1402)*",
        parse_mode="Markdown"
    )
    await callback.answer()

@router.message(EditProfileState.address, F.text)
async def process_address_input(message: types.Message, state: FSMContext):
    address = message.text.strip()
    user_id = message.from_user.id

    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.telegram_id == user_id)
        res = await session.execute(stmt)
        user = res.scalar_one_or_none()
        if user:
            user.delivery_address = address
            await session.commit()

    await state.clear()
    await message.answer(f"✅ **Адрес доставки сохранен!**\n📍 `{address}`", parse_mode="Markdown")

@router.callback_query(F.data == "edit_profile_city_select")
async def select_city_callback(callback: types.CallbackQuery):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🏙️ Нячанг", callback_data="set_city:Нячанг"),
                InlineKeyboardButton(text="🏙️ Дананг", callback_data="set_city:Дананг")
            ],
            [
                InlineKeyboardButton(text="🏙️ Сайгон (Хошимин)", callback_data="set_city:Сайгон"),
                InlineKeyboardButton(text="🏝️ Фукуок", callback_data="set_city:Фукуок")
            ]
        ]
    )
    await callback.message.answer("🏙️ Выберите ваш город в Вьетнаме:", reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data.startswith("set_city:"))
async def set_city_action(callback: types.CallbackQuery):
    city = callback.data.split(":")[1]
    user_id = callback.from_user.id

    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.telegram_id == user_id)
        res = await session.execute(stmt)
        user = res.scalar_one_or_none()
        if user:
            user.city = city
            await session.commit()

    await callback.answer(f"✅ Город {city} сохранен!", show_alert=True)

@router.callback_query(F.data == "edit_profile_pvz_select")
async def select_pvz_callback(callback: types.CallbackQuery):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🏢 Нячанг (Север / Pham Van Dong)", callback_data="set_pvz:Нячанг (Север)")
            ],
            [
                InlineKeyboardButton(text="🏢 Нячанг (Анвьен / Tran Phu)", callback_data="set_pvz:Нячанг (Анвьен)")
            ],
            [
                InlineKeyboardButton(text="🛵 Доставка курьером на адрес", callback_data="set_pvz:Курьерская доставка")
            ]
        ]
    )
    await callback.message.answer("🏢 Выберите удобный пункт выдачи (ПВЗ):", reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data.startswith("set_pvz:"))
async def set_pvz_action(callback: types.CallbackQuery):
    pvz = callback.data.split(":")[1]
    user_id = callback.from_user.id

    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.telegram_id == user_id)
        res = await session.execute(stmt)
        user = res.scalar_one_or_none()
        if user:
            user.preferred_pvz = pvz
            await session.commit()

    await callback.answer(f"✅ ПВЗ {pvz} выбран!", show_alert=True)
