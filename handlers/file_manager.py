import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from config import settings
from database.models import Project
from file_manager.editor import read_file, write_file

fm_router = Router()

class FileManagerStates(StatesGroup):
    browsing = State()
    waiting_for_file_edit = State()
    waiting_for_new_folder_name = State()

def get_fm_keyboard(current_path: str, project_dir: str, project_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    
    if current_path != project_dir:
        parent = os.path.dirname(current_path)
        kb.button(text="📁 .. (Up)", callback_data=f"fm_nav_{project_id}_{parent}")

    try:
        items = os.listdir(current_path)
    except Exception:
        items = []

    for item in items:
        full_path = os.path.join(current_path, item)
        if os.path.isdir(full_path):
            kb.button(text=f"📁 {item}", callback_data=f"fm_nav_{project_id}_{full_path}")
        else:
            kb.button(text=f"📄 {item}", callback_data=f"fm_file_{project_id}_{full_path}")
            
    kb.button(text="➕ New Folder", callback_data=f"fm_mkdir_{project_id}_{current_path}")
    kb.button(text="🔙 Back to Project", callback_data=f"proj_manage_{project_id}")
    kb.adjust(1)
    return kb.as_markup()

@fm_router.callback_query(F.data.startswith("fm_browse_"))
async def open_file_manager(call: CallbackQuery, state: FSMContext, session):
    project_id = int(call.data.split("_")[2])
    project = await session.get(Project, project_id)
    if not project:
        await call.answer("Project not found.", show_alert=True)
        return
        
    project_dir = os.path.join(settings.PROJECTS_DIR, f"{project.owner.telegram_id}_{project.name}")
    await state.update_data(current_path=project_dir, project_dir=project_dir, project_id=project_id)
    await state.set_state(FileManagerStates.browsing)
    
    await call.message.edit_text(
        f"📁 **File Manager**\nProject: `{project.name}`\nPath: `/`",
        reply_markup=get_fm_keyboard(project_dir, project_dir, project_id),
        parse_mode="Markdown"
    )

@fm_router.callback_query(F.data.startswith("fm_nav_"))
async def navigate_directory(call: CallbackQuery, state: FSMContext):
    parts = call.data.split("_", 2)
    project_id = int(parts[1])
    target_path = parts[2]
    
    data = await state.get_data()
    project_dir = data.get("project_dir")
    
    # Path traversal protection
    if not os.path.abspath(target_path).startswith(os.path.abspath(project_dir)):
        await call.answer("Access Denied.", show_alert=True)
        return

    await state.update_data(current_path=target_path)
    display_path = target_path.replace(project_dir, "") or "/"
    
    await call.message.edit_text(
        f"📁 **File Manager**\nPath: `{display_path}`",
        reply_markup=get_fm_keyboard(target_path, project_dir, project_id),
        parse_mode="Markdown"
    )

@fm_router.callback_query(F.data.startswith("fm_file_"))
async def manage_file(call: CallbackQuery, state: FSMContext):
    parts = call.data.split("_", 2)
    file_path = parts[2]
    
    kb = InlineKeyboardBuilder()
    kb.button(text="📥 Download", callback_data=f"fm_dl_{file_path}")
    kb.button(text="✏️ Edit", callback_data=f"fm_edit_{file_path}")
    kb.button(text="🗑 Delete", callback_data=f"fm_del_{file_path}")
    kb.button(text="🔙 Back", callback_data=f"fm_nav_{parts[1]}_{os.path.dirname(file_path)}")
    kb.adjust(2, 1, 1)
    
    await call.message.edit_text(f"📄 **File:** `{os.path.basename(file_path)}`", reply_markup=kb.as_markup(), parse_mode="Markdown")

@fm_router.callback_query(F.data.startswith("fm_dl_"))
async def download_file(call: CallbackQuery):
    file_path = call.data.split("_", 2)[2]
    if os.path.exists(file_path):
        await call.message.answer_document(FSInputFile(file_path))
    else:
        await call.answer("File not found.", show_alert=True)

@fm_router.callback_query(F.data.startswith("fm_edit_"))
async def edit_file(call: CallbackQuery, state: FSMContext):
    file_path = call.data.split("_", 2)[2]
    content = read_file(file_path)
    if content is None:
        await call.answer("Cannot read file. It might be binary.", show_alert=True)
        return
        
    await state.update_data(editing_file=file_path)
    await state.set_state(FileManagerStates.waiting_for_file_edit)
    await call.message.answer(f"✏️ Send the new content for `{os.path.basename(file_path)}`:\n\nCurrent Content:\n```\n{content[:3000]}\n```", parse_mode="Markdown")

@fm_router.message(FileManagerStates.waiting_for_file_edit)
async def save_edited_file(message: Message, state: FSMContext):
    data = await state.get_data()
    file_path = data.get("editing_file")
    
    if write_file(file_path, message.text):
        await message.answer("✅ File saved successfully!")
    else:
        await message.answer("❌ Error saving file.")
        
    await state.set_state(FileManagerStates.browsing)