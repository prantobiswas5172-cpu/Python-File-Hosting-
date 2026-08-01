import os
import re

ALLOWED_EXTENSIONS = {
    'py', 'js', 'json', 'txt', 'env', 'php', 'html', 'css', 
    'md', 'csv', 'sqlite', 'db', 'sh', 'yml', 'yaml', 'zip'
}

def validate_extension(filename: str) -> bool:
    """Extension whitelist validation."""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS

def is_safe_filename(filename: str) -> bool:
    """Command injection and shell bypass protection for filenames."""
    if re.search(r'[;&|`$><\\]', filename):
        return False
    if '..' in filename or filename.startswith('/'):
        return False
    return True