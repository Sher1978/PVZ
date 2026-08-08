import asyncio
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from app.models.user import User
from app.models.auction import Auction, AuctionBid

def format_vnd(amount: float | int | None) -> str:
    if amount is None:
        return "0 ₫"
    val = int(amount)
    return f"{val:,}".replace(",", " ") + " ₫"

def get_auction_card_caption(auction: Auction, user_id: Optional[int] = None, top_bidder_name: Optional[str] = None) -> str:
    end_str = auction.end_time.strftime("%H:%M:%S (%d.%m)") if auction.end_time else "не ограничено"
    
    status_header = ""
    if auction.status == "active":
        if auction.winner_id and user_id and auction.winner_id == user_id:
            status_header = "⭐ **Ваша ставка является фаворитной в данных торгах!**\n\n"
        status_line = "🟢 **ТОРГИ АКТИВНЫ**"
    elif auction.status == "completed":
        status_line = "🏁 **АУКЦИОН ЗАВЕРШЕН**"
    else:
        status_line = f"ℹ️ **СТАТУС: {auction.status.upper()}**"

    leader_str = f"@{top_bidder_name}" if top_bidder_name else "Пока нет ставок"
    if auction.status == "completed" and top_bidder_name:
        leader_str = f"👑 Победитель: @{top_bidder_name}"

    caption = (
        f"{status_header}"
        f"🔨 **СПЕЦ АУКЦИОН**\n\n"
        f"📌 **{auction.title}**\n\n"
        f"{auction.description or ''}\n\n"
        f"----------------------------------\n"
        f"💰 **Стартовая цена:** {format_vnd(auction.starting_price)}\n"
        f"⚡ **Выкупная цена:** {format_vnd(auction.buyout_price)}\n"
        f"📈 **Минимальный шаг:** {format_vnd(auction.min_bid_step)}\n\n"
        f"🔥 **ТЕКУЩАЯ ЦЕНА:** {format_vnd(auction.current_price)}\n"
        f"🏆 **Лидер:** {leader_str}\n"
        f"⏳ **Окончание:** {end_str}\n"
        f"----------------------------------\n"
        f"{status_line}\n"
    )
    return caption

def get_auction_keyboard(auction: Auction) -> InlineKeyboardMarkup:
    if auction.status == "active":
        buttons = [
            [
                InlineKeyboardButton(text="💸 Сделать ставку", callback_data=f"bid_click:{auction.id}"),
                InlineKeyboardButton(text=f"⚡ Выкупить за {format_vnd(auction.buyout_price)}", callback_data=f"buyout_click:{auction.id}")
            ],
            [
                InlineKeyboardButton(text="📜 Правила аукциона", callback_data="auction_rules"),
                InlineKeyboardButton(text="🔄 Обновить статус", callback_data=f"refresh_auction:{auction.id}")
            ]
        ]
    else:
        buttons = [
            [
                InlineKeyboardButton(text="📜 Правила аукциона", callback_data="auction_rules")
            ]
        ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_post_auction_sub_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ ДА, участвую!", callback_data="sub_auction:yes"),
                InlineKeyboardButton(text="❌ НЕТ, отписаться", callback_data="sub_auction:no")
            ]
        ]
    )

async def send_transient_message(bot: Bot, chat_id: int, text: str, delay: int = 5):
    """Sends a message below the card and auto-deletes it after delay seconds to keep chat clean."""
    try:
        msg = await bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")
        await asyncio.sleep(delay)
        await bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
    except Exception:
        pass

async def get_top_bidder_info(session: AsyncSession, auction_id: str) -> tuple[Optional[int], Optional[str]]:
    stmt = (
        select(AuctionBid)
        .where(AuctionBid.auction_id == auction_id)
        .order_by(AuctionBid.amount.desc(), AuctionBid.created_at.asc())
        .limit(1)
    )
    result = await session.execute(stmt)
    bid = result.scalar_one_or_none()
    if bid:
        name = bid.username or bid.user_name or f"User_{bid.user_id}"
        return bid.user_id, name
    return None, None

async def broadcast_auction_start(bot: Bot, session: AsyncSession, auction: Auction):
    stmt = select(User).where(User.is_auction_subscribed == True)
    res = await session.execute(stmt)
    subscribers = res.scalars().all()
    
    top_user_id, top_name = await get_top_bidder_info(session, auction.id)
    caption = get_auction_card_caption(auction, user_id=None, top_bidder_name=top_name)
    kb = get_auction_keyboard(auction)
    
    broadcast_dict = dict(auction.broadcast_messages or {})
    photos = auction.photos or []

    for user in subscribers:
        try:
            if photos:
                # Send primary photo as auction card
                msg = await bot.send_photo(
                    chat_id=user.telegram_id,
                    photo=photos[0],
                    caption=caption,
                    reply_markup=kb,
                    parse_mode="Markdown"
                )
            else:
                msg = await bot.send_message(
                    chat_id=user.telegram_id,
                    text=caption,
                    reply_markup=kb,
                    parse_mode="Markdown"
                )
            broadcast_dict[str(user.telegram_id)] = msg.message_id
        except (TelegramForbiddenError, TelegramBadRequest):
            continue
        except Exception as e:
            print(f"Error broadcasting to {user.telegram_id}: {e}")

    auction.broadcast_messages = broadcast_dict
    await session.commit()

async def update_all_broadcast_posts(bot: Bot, session: AsyncSession, auction: Auction):
    broadcast_dict = dict(auction.broadcast_messages or {})
    top_user_id, top_name = await get_top_bidder_info(session, auction.id)
    kb = get_auction_keyboard(auction)

    for user_id_str, msg_id in broadcast_dict.items():
        try:
            uid = int(user_id_str)
            caption = get_auction_card_caption(auction, user_id=uid, top_bidder_name=top_name)
            await bot.edit_message_caption(
                chat_id=uid,
                message_id=msg_id,
                caption=caption,
                reply_markup=kb,
                parse_mode="Markdown"
            )
        except TelegramBadRequest as e:
            if "message is not modified" in str(e):
                pass
        except Exception as e:
            print(f"Error updating post for user {user_id_str}: {e}")

async def place_bid(
    bot: Bot,
    session: AsyncSession,
    auction_id: str,
    user_id: int,
    user_name: str,
    username: Optional[str],
    amount: float
) -> tuple[bool, str, Optional[Auction]]:
    stmt = select(Auction).where(Auction.id == auction_id)
    res = await session.execute(stmt)
    auction = res.scalar_one_or_none()

    if not auction or auction.status != "active":
        return False, "Аукцион не активен.", None

    now = datetime.now(timezone.utc)
    if auction.end_time and auction.end_time <= now:
        await finish_auction(bot, session, auction_id)
        return False, "Время аукциона истекло!", None

    if amount >= float(auction.buyout_price):
        return await buyout_auction(bot, session, auction_id, user_id, user_name, username)

    min_required = float(auction.current_price) + float(auction.min_bid_step)
    if amount < min_required:
        return False, f"Минимальная ставка должна быть не менее {format_vnd(min_required)}", auction

    prev_top_user_id, prev_top_name = await get_top_bidder_info(session, auction.id)

    # Record new bid
    new_bid = AuctionBid(
        auction_id=auction_id,
        user_id=user_id,
        user_name=user_name,
        username=username,
        amount=amount
    )
    session.add(new_bid)
    auction.current_price = amount
    auction.winner_id = user_id
    auction.winning_bid = amount
    auction.winning_type = "bid"

    await session.commit()

    # Notify previous top bidder that their bid was beaten
    if prev_top_user_id and prev_top_user_id != user_id:
        asyncio.create_task(
            send_transient_message(
                bot,
                prev_top_user_id,
                f"⚠️ **Ваша ставка побита в торгах по «{auction.title}»!**\n\n"
                f"🔥 Текущая цена: **{format_vnd(amount)}**\n"
                f"Сделайте новую ставку, чтобы вернуть лидерство!",
                delay=7
            )
        )

    # Update all broadcast posts live
    asyncio.create_task(update_all_broadcast_posts(bot, session, auction))

    return True, "⭐ **Ваша ставка является фаворитной в данных торгах!**", auction

async def buyout_auction(
    bot: Bot,
    session: AsyncSession,
    auction_id: str,
    user_id: int,
    user_name: str,
    username: Optional[str]
) -> tuple[bool, str, Optional[Auction]]:
    stmt = select(Auction).where(Auction.id == auction_id)
    res = await session.execute(stmt)
    auction = res.scalar_one_or_none()

    if not auction or auction.status != "active":
        return False, "Аукцион не активен.", None

    now = datetime.now(timezone.utc)
    auction.status = "completed"
    auction.winner_id = user_id
    auction.winning_bid = auction.buyout_price
    auction.current_price = auction.buyout_price
    auction.winning_type = "buyout"
    auction.payment_deadline = now + timedelta(hours=1)

    # Save buyout bid
    buyout_bid = AuctionBid(
        auction_id=auction_id,
        user_id=user_id,
        user_name=user_name,
        username=username,
        amount=auction.buyout_price
    )
    session.add(buyout_bid)
    await session.commit()

    # Finish and notify winner and participants
    asyncio.create_task(finish_auction(bot, session, auction_id, is_buyout=True))
    return True, f"🎉 Вы выкупили товар по цене {format_vnd(auction.buyout_price)}!", auction

async def finish_auction(bot: Bot, session: AsyncSession, auction_id: str, is_buyout: bool = False):
    stmt = select(Auction).where(Auction.id == auction_id)
    res = await session.execute(stmt)
    auction = res.scalar_one_or_none()

    if not auction or auction.status == "completed_notified":
        return

    auction.status = "completed"
    now = datetime.now(timezone.utc)
    if not auction.payment_deadline:
        auction.payment_deadline = now + timedelta(hours=1)

    top_user_id, top_name = await get_top_bidder_info(session, auction.id)
    winner_str = f"@{top_name}" if top_name else "Никто"

    # Update broadcast messages across all chats with final results + Subscription preference buttons
    broadcast_dict = dict(auction.broadcast_messages or {})
    for user_id_str, msg_id in broadcast_dict.items():
        try:
            uid = int(user_id_str)
            if top_user_id and uid == top_user_id:
                winner_msg = (
                    f"🎉 **ПОЗДРАВЛЯЕМ С ПОБЕДОЙ!** 🎉\n\n"
                    f"Вы выиграли спец аукцион по товару:\n"
                    f"📌 **{auction.title}**\n"
                    f"💰 Финальная цена: **{format_vnd(auction.winning_bid or auction.current_price)}**\n\n"
                    f"⏳ **У вас есть 1 час** (до {auction.payment_deadline.strftime('%H:%M')}), "
                    f"чтобы указать адрес доставки и совершить оплату."
                )
                kb_winner = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(text="📍 Указать адрес и оплатить", callback_data=f"winner_checkout:{auction.id}")
                        ]
                    ]
                )
                await bot.edit_message_caption(
                    chat_id=uid,
                    message_id=msg_id,
                    caption=winner_msg,
                    reply_markup=kb_winner,
                    parse_mode="Markdown"
                )
            else:
                participant_msg = (
                    f"🏁 **АУКЦИОН ЗАВЕРШЕН**\n\n"
                    f"📌 Товар: **{auction.title}**\n"
                    f"👑 Победитель: **{winner_str}**\n"
                    f"💰 Финальная цена: **{format_vnd(auction.winning_bid or auction.current_price)}**\n\n"
                    f"👏 Желаем успеха в следующих торгах!\n\n"
                    f"🔔 **Участвую в следующих аукционах:**"
                )
                await bot.edit_message_caption(
                    chat_id=uid,
                    message_id=msg_id,
                    caption=participant_msg,
                    reply_markup=get_post_auction_sub_keyboard(),
                    parse_mode="Markdown"
                )
        except Exception as e:
            print(f"Error finishing broadcast for user {user_id_str}: {e}")

    auction.status = "completed_notified"
    await session.commit()
