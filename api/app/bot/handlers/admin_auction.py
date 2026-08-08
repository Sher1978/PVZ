from datetime import datetime, timedelta, timezone
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.models.auction import Auction
from app.services.auction_service import (
    format_vnd,
    broadcast_auction_start,
    send_transient_message
)

router = Router()

class CreateAuctionState(StatesGroup):
    photos = State()
    title = State()
    description = State()
    starting_price = State()
    min_bid_step = State()
    buyout_price = State()
    duration = State()
    confirm = State()

async def is_user_admin(user_id: int) -> bool:
    if user_id in settings.admin_ids_set or user_id in settings.superadmin_ids_set:
        return True
    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.telegram_id == user_id)
        res = await session.execute(stmt)
        user = res.scalar_one_or_none()
        if user:
            return user.is_admin or user.role in ("admin", "superadmin")
        return False

@router.message(Command("admin_auction"))
@router.callback_query(F.data == "admin_create_auction")
async def start_admin_auction_creation(event: types.Message | types.CallbackQuery, state: FSMContext):
    user_id = event.from_user.id
    if not await is_user_admin(user_id):
        text = "❌ У вас нет прав администратора для создания аукционов."
        if isinstance(event, types.CallbackQuery):
            await event.answer(text, show_alert=True)
        else:
            await event.answer(text)
        return

    await state.clear()
    await state.update_data(photos=[])
    await state.set_state(CreateAuctionState.photos)

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Готово (Завершить загрузку фото)")],
            [KeyboardButton(text="❌ Отмена")]
        ],
        resize_keyboard=True
    )

    msg_text = (
        "📸 **Создание товара для спец аукциона (Шаг 1 из 7)**\n\n"
        "Отправьте от 1 до 5 фотографий товара по одной.\n"
        "Когда закончите отправку фото, нажмите кнопку **«✅ Готово»**."
    )

    if isinstance(event, types.CallbackQuery):
        await event.message.answer(msg_text, reply_markup=kb, parse_mode="Markdown")
        await event.answer()
    else:
        await event.answer(msg_text, reply_markup=kb, parse_mode="Markdown")

@router.message(CreateAuctionState.photos, F.photo)
async def process_photo_upload(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])

    if len(photos) >= 5:
        await message.answer("⚠️ Вы уже загрузили максимальное количество фото (5). Нажмите «✅ Готово».")
        return

    photo_id = message.photo[-1].file_id
    photos.append(photo_id)
    await state.update_data(photos=photos)

    await message.answer(
        f"✅ Фото #{len(photos)} получено! (Всего: {len(photos)} из 5).\n"
        f"Отправьте следующее фото или нажмите **«✅ Готово»**."
    )

@router.message(CreateAuctionState.photos, F.text == "✅ Готово (Завершить загрузку фото)")
async def process_photos_finished(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])

    if not photos:
        await message.answer("⚠️ Необходимо загрузить хотя бы 1 фотографию товара!")
        return

    await state.set_state(CreateAuctionState.title)
    await message.answer(
        "📝 **Шаг 2 из 7: Название товара**\n\n"
        "Введите название товара для аукциона:",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )

@router.message(CreateAuctionState.photos, F.text == "❌ Отмена")
@router.message(F.text == "❌ Отмена")
async def cancel_auction_creation(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Создание аукциона отменено.", reply_markup=ReplyKeyboardRemove())

@router.message(CreateAuctionState.title)
async def process_title(message: types.Message, state: FSMContext):
    title = message.text.strip()
    if len(title) < 3:
        await message.answer("⚠️ Название слишком короткое. Введите понятное название:")
        return

    await state.update_data(title=title)
    await state.set_state(CreateAuctionState.description)
    await message.answer(
        "📄 **Шаг 3 из 7: Описание товара**\n\n"
        "Введите подробное описание товара (характеристики, состояние, условия):",
        parse_mode="Markdown"
    )

@router.message(CreateAuctionState.description)
async def process_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text.strip())
    await state.set_state(CreateAuctionState.starting_price)
    await message.answer(
        "💰 **Шаг 4 из 7: Стартовая цена (в ₫ / VND)**\n\n"
        "Введите стартовую цену (например: `500000` для 500 000 ₫):",
        parse_mode="Markdown"
    )

@router.message(CreateAuctionState.starting_price)
async def process_starting_price(message: types.Message, state: FSMContext):
    raw = message.text.replace(" ", "").replace("₫", "").replace("VND", "").strip()
    if not raw.isdigit() or int(raw) <= 0:
        await message.answer("⚠️ Пожалуйста, введите корректное число для стартовой цены (например: 500000):")
        return

    val = float(raw)
    await state.update_data(starting_price=val)
    await state.set_state(CreateAuctionState.min_bid_step)
    await message.answer(
        "📈 **Шаг 5 из 7: Минимальный шаг ставки (в ₫ / VND)**\n\n"
        "Введите минимальный шаг повышения цены (например: `50000` для 50 000 ₫):",
        parse_mode="Markdown"
    )

@router.message(CreateAuctionState.min_bid_step)
async def process_min_bid_step(message: types.Message, state: FSMContext):
    raw = message.text.replace(" ", "").replace("₫", "").replace("VND", "").strip()
    if not raw.isdigit() or int(raw) <= 0:
        await message.answer("⚠️ Пожалуйста, введите корректный шаг ставки (например: 50000):")
        return

    val = float(raw)
    await state.update_data(min_bid_step=val)
    await state.set_state(CreateAuctionState.buyout_price)
    data = await state.get_data()
    starting_price = data.get("starting_price", 0)

    await message.answer(
        f"⚡ **Шаг 6 из 7: Выкупная цена «Прямо сейчас» (в ₫ / VND)**\n\n"
        f"Стартовая цена: {format_vnd(starting_price)}\n"
        f"Введите финальную цену для мгновенного выкупа (должна быть выше стартовой, например: `2000000`):",
        parse_mode="Markdown"
    )

@router.message(CreateAuctionState.buyout_price)
async def process_buyout_price(message: types.Message, state: FSMContext):
    raw = message.text.replace(" ", "").replace("₫", "").replace("VND", "").strip()
    data = await state.get_data()
    starting_price = data.get("starting_price", 0)

    if not raw.isdigit() or float(raw) <= starting_price:
        await message.answer(f"⚠️ Выкупная цена должна быть числом и быть строго выше стартовой ({format_vnd(starting_price)}):")
        return

    val = float(raw)
    await state.update_data(buyout_price=val)
    await state.set_state(CreateAuctionState.duration)
    await message.answer(
        "⏳ **Шаг 7 из 7: Время торгов (длительность в минутах)**\n\n"
        "Укажите длительность аукциона в минутах (например: `60` для 1 часа, `120` для 2 часов, `1440` для 24 часов):",
        parse_mode="Markdown"
    )

@router.message(CreateAuctionState.duration)
async def process_duration(message: types.Message, state: FSMContext):
    raw = message.text.strip()
    if not raw.isdigit() or int(raw) <= 0:
        await message.answer("⚠️ Пожалуйста, укажите количество минут положительным числом (например: 60):")
        return

    duration_minutes = int(raw)
    await state.update_data(duration_minutes=duration_minutes)
    data = await state.get_data()

    summary_text = (
        "📋 **ПРЕДПРОСМОТР КАРТОЧКИ АУКЦИОНА**\n\n"
        f"📌 **Название:** {data['title']}\n"
        f"📄 **Описание:** {data['description']}\n"
        f"📸 **Фотографий:** {len(data['photos'])}\n\n"
        f"💰 **Стартовая цена:** {format_vnd(data['starting_price'])}\n"
        f"📈 **Минимальный шаг:** {format_vnd(data['min_bid_step'])}\n"
        f"⚡ **Выкупная цена:** {format_vnd(data['buyout_price'])}\n"
        f"⏳ **Длительность:** {duration_minutes} минут\n\n"
        "Запустить аукцион прямо сейчас?"
    )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🚀 ЗАПУСТИТЬ АУКЦИОН", callback_data="confirm_launch_auction")
            ],
            [
                InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_launch_auction")
            ]
        ]
    )

    await state.set_state(CreateAuctionState.confirm)
    await message.answer(summary_text, reply_markup=kb, parse_mode="Markdown")

@router.callback_query(CreateAuctionState.confirm, F.data == "confirm_launch_auction")
async def confirm_launch_auction_handler(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.clear()

    now = datetime.now(timezone.utc)
    end_time = now + timedelta(minutes=data['duration_minutes'])

    async with AsyncSessionLocal() as session:
        new_auction = Auction(
            title=data['title'],
            description=data['description'],
            photos=data['photos'],
            starting_price=data['starting_price'],
            current_price=data['starting_price'],
            buyout_price=data['buyout_price'],
            min_bid_step=data['min_bid_step'],
            status="active",
            start_time=now,
            end_time=end_time
        )
        session.add(new_auction)
        await session.commit()
        await session.refresh(new_auction)

        # Broadcast auction start to all subscribers
        await callback.message.edit_text("🚀 **Аукцион запущен! Рассылка участникам начата...**", parse_mode="Markdown")
        await broadcast_auction_start(callback.bot, session, new_auction)

    await callback.answer("✅ Аукцион успешно запущен!", show_alert=True)

@router.callback_query(CreateAuctionState.confirm, F.data == "cancel_launch_auction")
async def cancel_launch_auction_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Создание и запуск аукциона отменены.")
    await callback.answer()
