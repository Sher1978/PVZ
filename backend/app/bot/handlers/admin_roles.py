from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.config import settings
from app.db.session import AsyncSessionLocal
from app.models.user import User

router = Router()

class AssignRoleState(StatesGroup):
    target_user = State()

async def is_user_superadmin(user_id: int) -> bool:
    if user_id in settings.superadmin_ids_set:
        return True
    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.telegram_id == user_id, User.role == "superadmin")
        res = await session.execute(stmt)
        return res.scalar_one_or_none() is not None

@router.message(Command("roles"))
@router.callback_query(F.data == "manage_roles_menu")
async def roles_menu_handler(event: types.Message | types.CallbackQuery, state: FSMContext):
    user_id = event.from_user.id
    if not await is_user_superadmin(user_id):
        text = "❌ Назначать роли может только **Суперадмин**."
        if isinstance(event, types.CallbackQuery):
            await event.answer(text, show_alert=True)
        else:
            await event.answer(text, parse_mode="Markdown")
        return

    await state.clear()
    async with AsyncSessionLocal() as session:
        stmt = select(User).where(
            or_(User.role.in_(["superadmin", "admin", "staff"]), User.is_admin == True)
        )
        res = await session.execute(stmt)
        staff_list = res.scalars().all()

    text = "👑 **УПРАВЛЕНИЕ РОЛЯМИ (СУПЕРАДМИН)**\n\n"
    if not staff_list:
        text += "В системе пока нет назначенных администраторов или стаффа.\n"
    else:
        text += "**Текущая команда и роли:**\n"
        for u in staff_list:
            role_emoji = {
                "superadmin": "👑 [СУПЕРАДМИН]",
                "admin": "⭐️ [АДМИНИСТРАТОР]",
                "staff": "📦 [СТАФФ / ВЫДАЧА]",
                "user": "👤 [ПОЛЬЗОВАТЕЛЬ]"
            }.get(u.role, "👤 [ПОЛЬЗОВАТЕЛЬ]")
            name = f"@{u.username}" if u.username else u.first_name
            text += f"• {role_emoji} {name} (ID: `{u.telegram_id}`)\n"

    text += "\nНажмите **«➕ Назначить роль»**, чтобы добавить администратора или сотрудника стаффа."

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="➕ Назначить роль", callback_data="start_assign_role"),
                InlineKeyboardButton(text="🔄 Обновить", callback_data="manage_roles_menu")
            ]
        ]
    )

    if isinstance(event, types.CallbackQuery):
        await event.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
        await event.answer()
    else:
        await event.answer(text, reply_markup=kb, parse_mode="Markdown")

@router.callback_query(F.data == "start_assign_role")
async def start_assign_role_handler(callback: types.CallbackQuery, state: FSMContext):
    if not await is_user_superadmin(callback.from_user.id):
        await callback.answer("❌ Доступно только Суперадмину.", show_alert=True)
        return

    await state.set_state(AssignRoleState.target_user)
    await callback.message.edit_text(
        "👤 **Назначение роли**\n\n"
        "Введите **Telegram ID** пользователя (например: `123456789`) или его **@username** (например: `@username`):",
        parse_mode="Markdown"
    )
    await callback.answer()

@router.message(AssignRoleState.target_user)
async def process_target_user(message: types.Message, state: FSMContext):
    query_val = message.text.strip()
    clean_username = query_val.lstrip("@")

    async with AsyncSessionLocal() as session:
        if query_val.isdigit():
            stmt = select(User).where(User.telegram_id == int(query_val))
        else:
            stmt = select(User).where(User.username.ilike(clean_username))
        
        res = await session.execute(stmt)
        target_user = res.scalar_one_or_none()

    if not target_user:
        await message.answer(
            f"❌ Пользователь `{query_val}` не найден в базе данных бота.\n"
            f"Попросите пользователя сначала запустить бота `/start`.",
            parse_mode="Markdown"
        )
        return

    await state.clear()
    name = f"@{target_user.username}" if target_user.username else target_user.first_name
    current_role = target_user.role or "user"

    text = (
        f"👤 **Пользователь найден:** {name}\n"
        f"🆔 ID: `{target_user.telegram_id}`\n"
        f"🎭 Текущая роль: **{current_role.upper()}**\n\n"
        f"Выберите новую роль для пользователя:"
    )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⭐️ АДМИНИСТРАТОР", callback_data=f"set_role:{target_user.telegram_id}:admin")
            ],
            [
                InlineKeyboardButton(text="📦 СТАФФ (Выдача товара)", callback_data=f"set_role:{target_user.telegram_id}:staff")
            ],
            [
                InlineKeyboardButton(text="👤 ОБЫЧНЫЙ ПОЛЬЗОВАТЕЛЬ", callback_data=f"set_role:{target_user.telegram_id}:user")
            ],
            [
                InlineKeyboardButton(text="❌ Отмена", callback_data="manage_roles_menu")
            ]
        ]
    )

    await message.answer(text, reply_markup=kb, parse_mode="Markdown")

@router.callback_query(F.data.startswith("set_role:"))
async def set_role_callback(callback: types.CallbackQuery):
    if not await is_user_superadmin(callback.from_user.id):
        await callback.answer("❌ Назначать роли может только Суперадмин.", show_alert=True)
        return

    parts = callback.data.split(":")
    target_id = int(parts[1])
    new_role = parts[2]

    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.telegram_id == target_id)
        res = await session.execute(stmt)
        target_user = res.scalar_one_or_none()

        if not target_user:
            await callback.answer("❌ Пользователь не найден.", show_alert=True)
            return

        target_user.role = new_role
        target_user.is_admin = (new_role in ["admin", "superadmin"])
        await session.commit()

        # Try to notify target user of their role update
        role_titles = {
            "admin": "⭐️ Администратор аукционов",
            "staff": "📦 Сотрудник стаффа (Выдача товара)",
            "user": "👤 Пользователь"
        }
        title = role_titles.get(new_role, new_role)

        try:
            await callback.bot.send_message(
                chat_id=target_id,
                text=f"🔔 **Вам назначена новая роль в боте:**\n\n🎭 **{title}**",
                parse_mode="Markdown"
            )
        except Exception:
            pass

    await callback.answer(f"✅ Роль успешно изменена на {new_role.upper()}!", show_alert=True)
    # Return to role menu
    await roles_menu_handler(callback, FSMContext)
