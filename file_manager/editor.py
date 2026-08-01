import os
import shutil
from .utils import validate_path

def create_folder(base_dir: str, folder_name: str) -> bool:
    """Creates a new directory inside the project securely."""
    target_path = os.path.join(base_dir, folder_name)
    if validate_path(base_dir, target_path):
        os.makedirs(target_path, exist_ok=True)
        return True
    return False

def delete_folder(base_dir: str, folder_name: str) -> bool:
    """Deletes a directory securely."""
    target_path = os.path.join(base_dir, folder_name)
    if validate_path(base_dir, target_path) and os.path.exists(target_path):
        shutil.rmtree(target_path)
        return True
    return False

def read_text_file(base_dir: str, file_path: str) -> str:
    """Reads a text file (.env, .py, .js) securely."""
    target_path = os.path.join(base_dir, file_path)
    if validate_path(base_dir, target_path) and os.path.isfile(target_path):
        with open(target_path, 'r', encoding='utf-8') as f:
            return f.read()
    raise FileNotFoundError("File not found or access denied.")

def write_text_file(base_dir: str, file_path: str, content: str) -> bool:
    """Writes to a text file securely."""
    target_path = os.path.join(base_dir, file_path)
    if validate_path(base_dir, target_path):
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False