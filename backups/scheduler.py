import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.db import async_session
from database.models import Project
from sqlalchemy import select
from file_manager.utils import backup_project
from config import settings
from logs.logger import get_logger

logger = get_logger("bot")

async def automated_daily_backup():
    """Iterates through all projects and generates ZIP backups."""
    logger.info("Starting automated daily backup process...")
    async with async_session() as session:
        result = await session.execute(select(Project))
        projects = result.scalars().all()
        
        for project in projects:
            project_dir = os.path.join(settings.PROJECTS_DIR, f"{project.owner.telegram_id}_{project.name}")
            if os.path.exists(project_dir):
                try:
                    backup_path = backup_project(f"daily_{project.name}_{project.id}", project_dir)
                    logger.info(f"Successfully backed up project ID {project.id} to {backup_path}")
                except Exception as e:
                    logger.error(f"Failed to backup project ID {project.id}: {e}")

def setup_backup_scheduler() -> AsyncIOScheduler:
    """Configures the APScheduler for Cron Jobs."""
    scheduler = AsyncIOScheduler()
    # Runs every day at 2:00 AM server time
    scheduler.add_job(automated_daily_backup, 'cron', hour=2, minute=0)
    return scheduler