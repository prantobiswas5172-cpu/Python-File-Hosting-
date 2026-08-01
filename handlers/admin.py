from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from config import settings
from utils.keyboards import admin_kb
from database.models import User, Project
from sqlalchemy import select, func, update
import asyncio

admin_router = Router()

class AdminStates(StatesGroup):
    waiting_for_broadcast = State()
    waiting_for_user_id_ban = State()
    waiting_for_user_id_vip = State()

def is_admin(telegram_id: int) -> bool:
    return telegram_id in settings.ADMIN_IDS

@admin_router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id): return
    await message.answer("👑 **Admin Panel**", reply_markup=admin_kb(), parse_mode="Markdown")

@admin_router.callback_query(F.data == "admin_stats")
async def admin_system_stats(call: CallbackQuery):
    if not is_admin(call.from_user.id): return
    from utils.system_monitor import get_system_stats
    await call.message.edit_text(get_system_stats(), reply_markup=admin_kb(), parse_mode="Markdown")

@admin_router.callback_query(F.data == "admin_users")
async def admin_users_stats(call: CallbackQuery, session):
    if not is_admin(call.from_user.id): return
    users_count = await session.scalar(select(func.count(User.id)))
    projects_count = await session.scalar(select(func.count(Project.id)))
    await call.message.edit_text(f"👥 **Total Users:** {users_count}\n🌐 **Total Projects:** {projects_count}", reply_markup=admin_kb(), parse_mode="Markdown")

@admin_router.callback_query(F.data == "admin_broadcast")
async def request_broadcast(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id): return
    await call.message.answer("📢 Send the message you want to broadcast to all users. Send /cancel to abort.")
    await state.set_state(AdminStates.waiting_for_broadcast)

@admin_router.message(AdminStates.waiting_for_broadcast)
async def process_broadcast(message: Message, state: FSMContext, session, bot: Bot):
    if not is_admin(message.from_user.id): return
    
    result = await session.execute(select(User))
    users = result.scalars().all()
    
    sent_count = 0
    msg = await message.answer("⏳ Broadcasting message...")
    
    for user in users:
        try:
            await bot.send_message(user.telegram_id, f"📢 **System Announcement**\n\n{message.text}", parse_mode="Markdown")
            sent_count += 1
            await asyncio.sleep(0.05) # Prevent flood wait
        except:
            pass # User blocked bot
            
    await msg.edit_text(f"✅ Broadcast sent to {sent_count} users.")
    await state.clear()

@admin_router.message(Command("grant_vip"))
async def grant_vip_cmd(message: Message, session):
    if not is_admin(message.from_user.id): return
    try:
        target_id = int(message.text.split(" ")[1])
        await session.execute(update(User).where(User.telegram_id == target_id).values(
            plan="VIP", 
            # Give higher limits conceptually (actual enforcement checks the 'plan' field)
        ))
        await session.commit()
        await message.answer(f"✅ User {target_id} upgraded to VIP!")
    except IndexError:
        await message.answer("Usage: /grant_vip <telegram_id>")

@admin_router.message(Command("ban"))
async def ban_cmd(message: Message, session):
    if not is_admin(message.from_user.id): return
    try:
        target_id = int(message.text.split(" ")[1])
        await session.execute(update(User).where(User.telegram_id == target_id).values(is_banned=True))
        await session.commit()
        await message.answer(f"🔨 User {target_id} has been banned.")
    except IndexError:
        await message.answer("Usage: /ban <telegram_id>")