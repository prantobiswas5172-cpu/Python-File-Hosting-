import os
import time
import logging
from config import settings
from file_manager.utils import backup_project

logger = logging.getLogger("hosting.backups")

def rotate_backups(project_name: str, max_backups: int = 3):
    """Deletes old backups keeping only the most recent 'max_backups'."""
    try:
        backups = []
        for file in os.listdir(settings.BACKUPS_DIR):
            if file.startswith(project_name) and file.endswith(".zip"):
                full_path = os.path.join(settings.BACKUPS_DIR, file)
                backups.append((full_path, os.path.getmtime(full_path)))
        
        # Sort by modification time, oldest first
        backups.sort(key=lambda x: x[1])
        
        while len(backups) > max_backups:
            oldest_backup = backups.pop(0)[0]
            os.remove(oldest_backup)
            logger.info(f"Rotated old backup: {oldest_backup}")
    except Exception as e:
        logger.error(f"Failed to rotate backups for {project_name}: {e}")

async def auto_backup_job(session_maker):
    """Cron job function to backup all running projects daily."""
    logger.info("Starting automated daily backups...")
    from database.models import Project
    from sqlalchemy import select
    
    try:
        async with session_maker() as session:
            result = await session.execute(select(Project).where(Project.status == "running"))
            projects = result.scalars().all()
            
            for project in projects:
                project_dir = os.path.join(settings.PROJECTS_DIR, f"{project.owner.telegram_id}_{project.name}")
                if os.path.exists(project_dir):
                    backup_project(project.name, project_dir)
                    rotate_backups(project.name, max_backups=3)
                    
        logger.info("Daily backups completed successfully.")
    except Exception as e:
        logger.error(f"Automated backup job failed: {e}")