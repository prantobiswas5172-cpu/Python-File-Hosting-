import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from database.models import Project
from config import settings
from hosting.git_manager import clone_repo, pull_repo
from file_manager.utils import detect_project_type

github_router = Router()

class GithubStates(StatesGroup):
    waiting_for_repo_url = State()

@github_router.callback_query(F.data.startswith("github_clone_"))
async def request_github_clone(call: CallbackQuery, state: FSMContext):
    project_id = int(call.data.split("_")[2])
    await state.update_data(project_id=project_id)
    await call.message.answer("🔗 Send the **HTTP URL** of the public GitHub repository you want to clone into this project.\n*(e.g., https://github.com/user/repo.git)*\n\nSend /cancel to abort.", parse_mode="Markdown")
    await state.set_state(GithubStates.waiting_for_repo_url)

@github_router.message(GithubStates.waiting_for_repo_url, F.text)
async def process_github_clone(message: Message, state: FSMContext, session):
    repo_url = message.text.strip()
    if not repo_url.startswith("http"):
        await message.answer("Please send a valid HTTP URL.")
        return

    data = await state.get_data()
    project = await session.get(Project, data["project_id"])
    
    project_dir = os.path.join(settings.PROJECTS_DIR, f"{project.owner.telegram_id}_{project.name}")
    
    msg = await message.answer("⏳ Cloning repository...")
    try:
        clone_repo(repo_url, project_dir)
        lang = detect_project_type(project_dir)
        project.lang = lang
        await session.commit()
        await msg.edit_text(f"✅ Repository cloned successfully!\nDetected Language: {lang.upper()}")
    except Exception as e:
        await msg.edit_text(f"❌ Failed to clone repository.\nError: `{str(e)}`", parse_mode="Markdown")
        
    await state.clear()

@github_router.callback_query(F.data.startswith("github_pull_"))
async def process_github_pull(call: CallbackQuery, session):
    project_id = int(call.data.split("_")[2])
    project = await session.get(Project, project_id)
    project_dir = os.path.join(settings.PROJECTS_DIR, f"{project.owner.telegram_id}_{project.name}")
    
    if not os.path.exists(os.path.join(project_dir, ".git")):
        await call.answer("No Git repository initialized here.", show_alert=True)
        return
        
    try:
        pull_repo(project_dir)
        await call.answer("✅ Successfully pulled latest changes!", show_alert=True)
    except Exception as e:
        await call.message.answer(f"❌ Git pull failed: `{str(e)}`", parse_mode="Markdown")