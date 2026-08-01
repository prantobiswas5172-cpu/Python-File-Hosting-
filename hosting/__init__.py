"""
Hosting Module Initialization
Exposes the Docker container manager and Git operations for the Cloud Hosting platform.
"""

from .docker_manager import DockerManager, docker_manager
from .git_manager import clone_repo, pull_repo

__all__ = [
    "DockerManager",
    "docker_manager",
    "clone_repo",
    "pull_repo"
]
