import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy import select
from database.models import Project
from config import settings
from utils.keyboards import project_manage_kb, dashboard_kb
from file_manager.utils import extract_zip, detect_project_type, backup_project
from hosting.docker_manager import docker_manager

project_router = Router()

class ProjectStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_zip = State()

@project_router.callback_query(F.data == "my_projects")
async def my_projects(call: CallbackQuery, session, db_user):
    result = await session.execute(select(Project).where(Project.user_id == db_user.id))
    projects = result.scalars().all()
    
    if not projects:
        await call.message.edit_text("You don't have any projects yet.", reply_markup=dashboard_kb())
        return

    text = "📁 **Your Projects:**\n\n"
    for p in projects:
        text += f"🔹 /{p.id} - {p.name} [{p.status.upper()}]\n"
    text += "\nSend /<id> to manage a project."
    await call.message.edit_text(text, parse_mode="Markdown", reply_markup=dashboard_kb())

@project_router.callback_query(F.data == "create_project")
async def create_project(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Enter a name for your new project (no spaces, alphanumeric):")
    await state.set_state(ProjectStates.waiting_for_name)

@project_router.message(ProjectStates.waiting_for_name)
async def process_project_name(message: Message, state: FSMContext, session, db_user):
    name = message.text.lower().strip()
    # Apply Limits (Simplified check)
    result = await session.execute(select(Project).where(Project.user_id == db_user.id))
    if len(result.scalars().all()) >= 1 and db_user.plan == "Free":
        await message.answer("⚠️ Free plan allows only 1 project. Upgrade to Premium.")
        await state.clear()
        return

    project_dir = os.path.join(settings.PROJECTS_DIR, f"{db_user.telegram_id}_{name}")
    os.makedirs(project_dir, exist_ok=True)

    new_project = Project(user_id=db_user.id, name=name)
    session.add(new_project)
    await session.commit()

    await state.update_data(project_id=new_project.id, project_dir=project_dir)
    await message.answer(f"Project '{name}' created!\nNow, please send your project files as a **.zip** archive.", parse_mode="Markdown")
    await state.set_state(ProjectStates.waiting_for_zip)

@project_router.message(ProjectStates.waiting_for_zip, F.document)
async def process_project_zip(message: Message, state: FSMContext, session, bot):
    if not message.document.file_name.endswith('.zip'):
        await message.answer("Please send a valid .zip file.")
        return

    data = await state.get_data()
    project_id = data['project_id']
    project_dir = data['project_dir']
    
    msg = await message.answer("📥 Downloading archive...")
    
    file = await bot.get_file(message.document.file_id)
    zip_path = os.path.join(project_dir, "upload.zip")
    await bot.download_file(file.file_path, zip_path)
    
    await msg.edit_text("📦 Extracting files...")
    extract_zip(zip_path, project_dir)
    
    lang = detect_project_type(project_dir)
    
    # Update DB
    project = await session.get(Project, project_id)
    project.lang = lang
    await session.commit()
    
    await msg.edit_text(f"✅ Upload complete!\nDetected language: **{lang.upper()}**\n\nManage your project below:", 
                        reply_markup=project_manage_kb(project_id, project.status), parse_mode="Markdown")
    await state.clear()

@project_router.message(F.text.startswith('/'))
async def direct_manage(message: Message, session, db_user):
    try:
        pid = int(message.text[1:])
        project = await session.get(Project, pid)
        if project and project.user_id == db_user.id:
            text = (f"⚙️ **Project:** {project.name}\n"
                    f"**Lang:** {project.lang.upper()}\n"
                    f"**Status:** {project.status.upper()}\n"
                    f"**Limits:** {project.ram_limit_mb}MB RAM / {project.cpu_limit} CPU")
            await message.answer(text, reply_markup=project_manage_kb(project.id, project.status), parse_mode="Markdown")
    except ValueError:
        pass

@project_router.callback_query(F.data.startswith("proj_"))
async def manage_project_actions(call: CallbackQuery, session):
    action, pid = call.data.split('_')[1:3]
    project = await session.get(Project, int(pid))
    
    if not project:
        await call.answer("Project not found.", show_alert=True)
        return

    project_dir = os.path.join(settings.PROJECTS_DIR, f"{project.owner.telegram_id}_{project.name}")

    if action == "start":
        await call.message.edit_text("⏳ Starting container...")
        container_id = await docker_manager.create_and_start_container(
            project.name, project.lang, project_dir, project.ram_limit_mb, project.cpu_limit
        )
        project.container_id = container_id
        project.status = "running"
        await session.commit()
        await call.message.edit_text("✅ Project is now running!", reply_markup=project_manage_kb(project.id, "running"))

    elif action == "stop":
        await call.message.edit_text("⏳ Stopping container...")
        if project.container_id:
            await docker_manager.stop_container(project.container_id)
            await docker_manager.delete_container(project.container_id)
        project.status = "stopped"
        project.container_id = None
        await session.commit()
        await call.message.edit_text("🛑 Project stopped.", reply_markup=project_manage_kb(project.id, "stopped"))
        
    elif action == "restart":
        await call.message.edit_text("🔄 Restarting...")
        if project.container_id:
            await docker_manager.stop_container(project.container_id)
            await docker_manager.delete_container(project.container_id)
        container_id = await docker_manager.create_and_start_container(
            project.name, project.lang, project_dir, project.ram_limit_mb, project.cpu_limit
        )
        project.container_id = container_id
        project.status = "running"
        await session.commit()
        await call.message.edit_text("✅ Restart complete!", reply_markup=project_manage_kb(project.id, "running"))

    elif action == "logs":
        if not project.container_id:
            await call.answer("Project is not running.", show_alert=True)
            return
        logs = await docker_manager.get_logs(project.container_id)
        await call.message.answer(f"📝 **Latest Logs:**\n```\n{logs[-3500:]}\n```", parse_mode="Markdown")

    elif action == "backup":
        await call.message.answer("⏳ Generating backup...")
        backup_path = backup_project(project.name, project_dir)
        await call.message.answer_document(FSInputFile(backup_path))
        os.remove(backup_path) # Clean up after sending

    elif action == "del":
        if project.container_id:
            await docker_manager.stop_container(project.container_id)
            await docker_manager.delete_container(project.container_id)
        import shutil
        if os.path.exists(project_dir):
            shutil.rmtree(project_dir)
        await session.delete(project)
        await session.commit()
        await call.message.edit_text("🗑 Project deleted.", reply_markup=dashboard_kb())