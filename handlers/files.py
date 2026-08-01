import os
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy import select
from database.models import Project
from config import settings
from file_manager.utils import validate_path
from security.validator import SecurityValidator

files_router = Router()

class FileManagerStates(StatesGroup):
    waiting_for_upload = State()
    waiting_for_env = State()

def generate_file_browser_kb(project_id: int, current_path: str, root_path: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    
    # List directories and files
    items = os.listdir(current_path)
    
    # Up directory button if not in root
    if os.path.abspath(current_path) != os.path.abspath(root_path):
        kb.button(text="⬆️ Up", callback_data=f"fm_up_{project_id}")

    for item in items:
        item_path = os.path.join(current_path, item)
        if os.path.isdir(item_path):
            kb.button(text=f"📁 {item}", callback_data=f"fm_noop")
        else:
            kb.button(text=f"📄 {item}", callback_data=f"fm_file_{project_id}_{item}")
            
    kb.button(text="📥 Upload File", callback_data=f"fm_upload_{project_id}")
    kb.button(text="📝 Edit .env", callback_data=f"fm_editenv_{project_id}")
    kb.button(text="🔙 Back to Project", callback_data=f"proj_logs_{project_id}") # Dummy back
    kb.adjust(1)
    return kb.as_markup()

@files_router.callback_query(F.data.startswith("proj_files_"))
async def open_file_manager(call: CallbackQuery, session):
    project_id = int(call.data.split("_")[2])
    project = await session.get(Project, project_id)
    
    if not project:
        await call.answer("Project not found.", show_alert=True)
        return

    project_dir = os.path.join(settings.PROJECTS_DIR, f"{project.owner.telegram_id}_{project.name}")
    if not os.path.exists(project_dir):
        await call.answer("Project directory is missing.", show_alert=True)
        return
        
    kb = generate_file_browser_kb(project.id, project_dir, project_dir)
    await call.message.edit_text(f"📁 **File Manager**: `{project.name}`\n\nSelect an action:", reply_markup=kb, parse_mode="Markdown")

@files_router.callback_query(F.data.startswith("fm_file_"))
async def download_file(call: CallbackQuery, session):
    parts = call.data.split("_")
    project_id = int(parts[2])
    filename = "_".join(parts[3:])
    
    project = await session.get(Project, project_id)
    project_dir = os.path.join(settings.PROJECTS_DIR, f"{project.owner.telegram_id}_{project.name}")
    target_file = os.path.join(project_dir, filename)
    
    if validate_path(project_dir, target_file) and os.path.exists(target_file):
        await call.message.answer_document(FSInputFile(target_file))
        await call.answer("File sent!")
    else:
        await call.answer("Access denied or file missing.", show_alert=True)

@files_router.callback_query(F.data.startswith("fm_upload_"))
async def request_file_upload(call: CallbackQuery, state: FSMContext):
    project_id = int(call.data.split("_")[2])
    await state.update_data(project_id=project_id)
    await call.message.answer("📤 Send the file you want to upload to the project root directory.\n\nSend /cancel to abort.")
    await state.set_state(FileManagerStates.waiting_for_upload)

@files_router.message(FileManagerStates.waiting_for_upload, F.document)
async def process_file_upload(message: Message, state: FSMContext, session, bot: Bot):
    data = await state.get_data()
    project_id = data.get("project_id")
    project = await session.get(Project, project_id)
    
    if not project or project.user_id != message.from_user.id:
        await message.answer("Unauthorized.")
        await state.clear()
        return

    filename = message.document.file_name
    if not SecurityValidator.is_extension_allowed(filename):
        await message.answer("❌ File extension not allowed for security reasons.")
        return

    project_dir = os.path.join(settings.PROJECTS_DIR, f"{project.owner.telegram_id}_{project.name}")
    target_path = os.path.join(project_dir, filename)
    
    if validate_path(project_dir, target_path):
        file = await bot.get_file(message.document.file_id)
        await bot.download_file(file.file_path, target_path)
        await message.answer(f"✅ File `{filename}` uploaded successfully!", parse_mode="Markdown")
    else:
        await message.answer("❌ Invalid path.")
    
    await state.clear()

@files_router.callback_query(F.data.startswith("fm_editenv_"))
async def request_env_edit(call: CallbackQuery, state: FSMContext):
    project_id = int(call.data.split("_")[2])
    await state.update_data(project_id=project_id)
    await call.message.answer("📝 Send the new content for your `.env` file.\nMake sure to format it as plain text.\n\nSend /cancel to abort.")
    await state.set_state(FileManagerStates.waiting_for_env)

@files_router.message(FileManagerStates.waiting_for_env, F.text)
async def save_env_file(message: Message, state: FSMContext, session):
    data = await state.get_data()
    project = await session.get(Project, data["project_id"])
    
    project_dir = os.path.join(settings.PROJECTS_DIR, f"{project.owner.telegram_id}_{project.name}")
    env_path = os.path.join(project_dir, ".env")
    
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(message.text.strip())
        
    await message.answer("✅ `.env` file saved successfully. Remember to restart your project!")
    await state.clear()