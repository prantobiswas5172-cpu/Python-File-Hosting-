from .user import user_router
from .project import project_router
from .admin import admin_router
from .files import files_router
from .github import github_router

__all__ = [
    "user_router",
    "project_router",
    "admin_router",
    "files_router",
    "github_router"
]
