import asyncio
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.models.auction import Auction
from app.services.auction_service import (
    format_vnd,
    place_bid,
    buyout_auction,
    get_auction_card_caption,
    get_auction_keyboard,
    get_top_bidder_info,
    send_transient_message
)

router = Router()

class EnterBidState(StatesGroup):
    auction_id = State()
    prompt_msg_id = State()

class WinnerAddressState(StatesGroup):
    auction_id = State()

AUCTION_RULES_TEXT = (
    "📜 **ПРАВИЛА АУКЦИОНА**\n\n"
    "1. **Ставки:** Каждая ставка должна быть выше текущей цены минимум на шаг аукциона.\n"
    "2. **Окончание:** Аукцион завершается либо по истечении таймера торгов, либо при мгновенном выкупе по фиксированной выкупной цене.\n"
    "3. **Победитель:** Победителем признается участник с наивысшей ставкой на момент финала или выкупивший товар мгновенно.\n"
    "4. **Оплата и Доставка:** Победитель обязан в течение **1 часа** определить адрес доставки в боте и произвести оплату.\n"
    "5. **Уведомления:** Система автоматически информирует участников, если их ставка перебита."
)

@router.message(Command("auction"))
@router.message(F.text == "🔨 АУКЦИОН")
@router.callback_query(F.data == "refresh_auction_menu")
async def main_auction_menu_handler(event: types.Message | types.CallbackQuery):
    user_id = event.from_user.id
    async with AsyncSessionLocal() as session:
        # Check active auction
        stmt = select(Auction).where(Auction.status == "active").order_by(Auction.created_at.desc()).limit(1)
        res = await session.execute(stmt)
        active_auction = res.scalar_one_or_none()

        # Check or create user record
        u_stmt = select(User).where(User.telegram_id == user_id)
        u_res = await session.execute(u_stmt)
        user = u_res.scalar_one_or_none()

        if not user:
            user = User(
                telegram_id=user_id,
                username=event.from_user.username,
                first_name=event.from_user.first_name
            )
            session.add(user)
            await session.commit()

        is_sub = user.is_auction_subscribed
        is_admin = user.is_admin or user.role in ("admin", "superadmin")
        is_superadmin = user.role == "superadmin"

    text = "🔨 **РАЗДЕЛ АУКЦИОН**\n\n"
    if active_auction:
        text += f"🟢 **Сейчас идут торги!**\n📌 Товар: **{active_auction.title}**\n🔥 Текущая цена: **{format_vnd(active_auction.current_price)}**\n\n"
    else:
        text += "ℹ️ В данный момент нет активных аукционов.\n\n"

    sub_status = "✅ Подписаны" if is_sub else "❌ Отписаны"
    text += f"🔔 **Статус подписки на рассылку:** {sub_status}\n"

    buttons = []
    if active_auction:
        buttons.append([InlineKeyboardButton(text="🎯 Перейти к текущему аукциону", callback_data=f"refresh_auction:{active_auction.id}")])
    
    buttons.append([InlineKeyboardButton(text="📜 Правила аукциона", callback_data="auction_rules")])
    
    sub_btn_text = "❌ Отписаться от аукционов" if is_sub else "🔔 Подписаться на аукционы"
    sub_action = "sub_auction:no" if is_sub else "sub_auction:yes"
    buttons.append([InlineKeyboardButton(text=sub_btn_text, callback_data=sub_action)])

    if is_superadmin:
        buttons.append([InlineKeyboardButton(text="👑 Управление ролями (Суперадмин)", callback_data="manage_roles_menu")])
    if is_admin:
        buttons.append([InlineKeyboardButton(text="🚀 Создать спец аукцион (Админ)", callback_data="admin_create_auction")])

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    if isinstance(event, types.CallbackQuery):
        await event.message.answer(text, reply_markup=kb, parse_mode="Markdown")
        await event.answer()
    else:
        await event.answer(text, reply_markup=kb, parse_mode="Markdown")

@router.callback_query(F.data == "auction_rules")
async def show_auction_rules_handler(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer(AUCTION_RULES_TEXT, parse_mode="Markdown")

@router.callback_query(F.data.startswith("sub_auction:"))
async def toggle_subscription_handler(callback: types.CallbackQuery):
    action = callback.data.split(":")[1]
    is_sub = (action == "yes")
    user_id = callback.from_user.id

    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.telegram_id == user_id)
        res = await session.execute(stmt)
        user = res.scalar_one_or_none()
        if user:
            user.is_auction_subscribed = is_sub
            await session.commit()

    status_text = "✅ Вы подписаны на новые аукционы!" if is_sub else "❌ Вы отписались от рассылки аукционов."
    await callback.answer(status_text, show_alert=True)

@router.callback_query(F.data.startswith("refresh_auction:"))
async def refresh_auction_handler(callback: types.CallbackQuery):
    auction_id = callback.data.split(":")[1]
    user_id = callback.from_user.id

    async with AsyncSessionLocal() as session:
        stmt = select(Auction).where(Auction.id == auction_id)
        res = await session.execute(stmt)
        auction = res.scalar_one_or_none()
        if not auction:
            await callback.answer("❌ Аукцион не найден.", show_alert=True)
            return

        top_user_id, top_name = await get_top_bidder_info(session, auction.id)
        caption = get_auction_card_caption(auction, user_id=user_id, top_bidder_name=top_name)
        kb = get_auction_keyboard(auction)

    try:
        await callback.message.edit_caption(caption=caption, reply_markup=kb, parse_mode="Markdown")
        await callback.answer("🔄 Статус обновлен!")
    except Exception:
        await callback.answer("🔄 Статус актуален!")

@router.callback_query(F.data.startswith("bid_click:"))
async def bid_click_handler(callback: types.CallbackQuery, state: FSMContext):
    auction_id = callback.data.split(":")[1]
    user_id = callback.from_user.id

    async with AsyncSessionLocal() as session:
        stmt = select(Auction).where(Auction.id == auction_id)
        res = await session.execute(stmt)
        auction = res.scalar_one_or_none()

    if not auction or auction.status != "active":
        await callback.answer("❌ Аукцион завершен или недоступен.", show_alert=True)
        return

    min_req = float(auction.current_price) + float(auction.min_bid_step)
    prompt = await callback.message.answer(
        f"💸 **Ввод ставки**\n\n"
        f"Текущая цена: **{format_vnd(auction.current_price)}**\n"
        f"Минимальная ставка: **{format_vnd(min_req)}**\n\n"
        f"Введите желаемую цену в ₫ (например: `{int(min_req)}`):",
        parse_mode="Markdown"
    )

    await state.set_state(EnterBidState.auction_id)
    await state.update_data(auction_id=auction_id, prompt_msg_id=prompt.message_id)
    await callback.answer()

@router.message(EnterBidState.auction_id)
async def process_user_bid_input(message: types.Message, state: FSMContext):
    data = await state.get_data()
    auction_id = data.get("auction_id")
    prompt_msg_id = data.get("prompt_msg_id")

    user_input = message.text.replace(" ", "").replace("₫", "").replace("VND", "").strip()

    # Automatically delete user message and prompt message to keep chat single-screen clean!
    try:
        await message.delete()
        if prompt_msg_id:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=prompt_msg_id)
    except Exception:
        pass

    await state.clear()

    if not user_input.isdigit() or float(user_input) <= 0:
        asyncio.create_task(
            send_transient_message(
                message.bot,
                message.chat.id,
                "⚠️ **Некорректная сумма.** Ставка должна быть положительным числом.",
                delay=4
            )
        )
        return

    bid_val = float(user_input)
    async with AsyncSessionLocal() as session:
        success, msg, auction = await place_bid(
            message.bot,
            session,
            auction_id,
            message.from_user.id,
            message.from_user.first_name,
            message.from_user.username,
            bid_val
        )

    asyncio.create_task(send_transient_message(message.bot, message.chat.id, msg, delay=5))

@router.callback_query(F.data.startswith("buyout_click:"))
async def buyout_click_handler(callback: types.CallbackQuery):
    auction_id = callback.data.split(":")[1]
    user_id = callback.from_user.id

    async with AsyncSessionLocal() as session:
        success, msg, auction = await buyout_auction(
            callback.bot,
            session,
            auction_id,
            user_id,
            callback.from_user.first_name,
            callback.from_user.username
        )

    await callback.answer(msg, show_alert=True)

@router.callback_query(F.data.startswith("winner_checkout:"))
async def winner_checkout_handler(callback: types.CallbackQuery, state: FSMContext):
    auction_id = callback.data.split(":")[1]
    await state.set_state(WinnerAddressState.auction_id)
    await state.update_data(auction_id=auction_id)

    await callback.message.answer(
        "📍 **Оформление заказа победителя**\n\n"
        "Пожалуйста, введите **полный адрес доставки** (город, улица, дом, квартиру/офис):",
        parse_mode="Markdown"
    )
    await callback.answer()

@router.message(WinnerAddressState.auction_id)
async def process_winner_address(message: types.Message, state: FSMContext):
    address = message.text.strip()
    data = await state.get_data()
    auction_id = data.get("auction_id")
    await state.clear()

    async with AsyncSessionLocal() as session:
        stmt = select(Auction).where(Auction.id == auction_id)
        res = await session.execute(stmt)
        auction = res.scalar_one_or_none()
        if auction:
            auction.winner_address = address
            auction.payment_status = "paid"  # Mark payment/checkout complete
            await session.commit()

    await message.answer(
        f"✅ **Адрес доставки сохранен!**\n\n"
        f"📍 **Адрес:** {address}\n"
        f"Ваш заказ передан на сборку и отправку. Спасибо за участие в аукционе!",
        parse_mode="Markdown"
    )
