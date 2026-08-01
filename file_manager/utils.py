import zipfile
import os
import shutil
from config import settings

def validate_path(base_dir: str, target_path: str) -> bool:
    """Path traversal protection"""
    abs_base = os.path.abspath(base_dir)
    abs_target = os.path.abspath(target_path)
    return abs_target.startswith(abs_base)

def extract_zip(zip_path: str, extract_to: str):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for member in zip_ref.namelist():
            target_path = os.path.join(extract_to, member)
            if validate_path(extract_to, target_path):
                zip_ref.extract(member, extract_to)
    os.remove(zip_path)

def detect_project_type(project_dir: str) -> str:
    files = os.listdir(project_dir)
    if "requirements.txt" in files or "main.py" in files or "bot.py" in files:
        return "python"
    elif "package.json" in files:
        return "nodejs"
    elif "index.php" in files:
        return "php"
    return "unknown"

def backup_project(project_name: str, source_dir: str) -> str:
    backup_name = f"{project_name}_backup"
    backup_path = os.path.join(settings.BACKUPS_DIR, backup_name)
    shutil.make_archive(backup_path, 'zip', source_dir)
    return f"{backup_path}.zip"