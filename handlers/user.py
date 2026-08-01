from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from utils.keyboards import dashboard_kb

user_router = Router()

@user_router.message(CommandStart())
async def start_cmd(message: Message, db_user):
    welcome_text = (f"👋 Welcome to **CloudHost Bot**, {message.from_user.first_name}!\n\n"
                    f"Deploy and manage your Python, Node.js, and PHP applications directly from Telegram.\n"
                    f"Your Plan: **{db_user.plan}**\n\n"
                    f"Select an option below to get started:")
    await message.answer(welcome_text, reply_markup=dashboard_kb(), parse_mode="Markdown")

@user_router.callback_query(F.data == "server_status")
async def server_status_cq(call: CallbackQuery):
    from utils.system_monitor import get_system_stats
    await call.message.edit_text(get_system_stats(), reply_markup=dashboard_kb(), parse_mode="Markdown")