from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def dashboard_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="📁 My Projects", callback_data="my_projects")
    kb.button(text="➕ Create Project", callback_data="create_project")
    kb.button(text="📊 Server Status", callback_data="server_status")
    kb.button(text="⚙️ Settings", callback_data="settings")
    kb.adjust(2, 2)
    return kb.as_markup()

def project_manage_kb(project_id: int, status: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if status == "running":
        kb.button(text="🛑 Stop", callback_data=f"proj_stop_{project_id}")
        kb.button(text="🔄 Restart", callback_data=f"proj_restart_{project_id}")
    else:
        kb.button(text="▶️ Start", callback_data=f"proj_start_{project_id}")
    
    kb.button(text="📝 Logs", callback_data=f"proj_logs_{project_id}")
    kb.button(text="📈 Statistics", callback_data=f"proj_stats_{project_id}")
    kb.button(text="💾 Backup", callback_data=f"proj_backup_{project_id}")
    kb.button(text="🗑 Delete", callback_data=f"proj_del_{project_id}")
    kb.button(text="🔙 Back", callback_data="my_projects")
    kb.adjust(2, 2, 2, 1, 1)
    return kb.as_markup()

def admin_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="👥 Users", callback_data="admin_users")
    kb.button(text="🌐 All Projects", callback_data="admin_projects")
    kb.button(text="📢 Broadcast", callback_data="admin_broadcast")
    kb.button(text="💻 Node Stats", callback_data="admin_stats")
    kb.adjust(2, 2)
    return kb.as_markup()