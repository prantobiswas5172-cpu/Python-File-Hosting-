import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    BOT_TOKEN: str
    ADMIN_IDS: list[int]
    DATABASE_URL: str = "sqlite+aiosqlite:///./hosting.db"
    PROJECTS_DIR: str = "/app/projects"
    BACKUPS_DIR: str = "/app/backups"
    WEBHOOK_PORT: int = 8080
    GITHUB_WEBHOOK_SECRET: str = "secret"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

# Ensure directories exist
os.makedirs(settings.PROJECTS_DIR, exist_ok=True)
os.makedirs(settings.BACKUPS_DIR, exist_ok=True)