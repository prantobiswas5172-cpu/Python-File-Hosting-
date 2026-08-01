import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

# Local imports
from config import settings
from database.db import init_db
from middlewares.auth import AuthMiddleware
from hosting.docker_manager import docker_manager
from backups.scheduler import setup_backup_scheduler
from deployment.github_webhook import start_webhook_server
from logs.logger import setup_logging, get_logger

# Routers
from handlers.user import user_router
from handlers.project import project_router
from handlers.admin import admin_router
from handlers.files import files_router
from handlers.github import github_router

# Initialize early logging
setup_logging()
logger = get_logger("bot")

async def set_bot_commands(bot: Bot):
    """Configures the Telegram Bot Command Menu."""
    commands = [
        BotCommand(command="start", description="Start the bot & open dashboard"),
        BotCommand(command="cancel", description="Cancel current operation"),
    ]
    await bot.set_my_commands(commands)

async def main():
    logger.info("Initializing Database...")
    await init_db()

    # Initialize Bot and Dispatcher
    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
    dp = Dispatcher()

    # Register Middlewares
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())

    # Register all Handlers/Routers
    dp.include_router(user_router)
    dp.include_router(project_router)
    dp.include_router(admin_router)
    dp.include_router(files_router)
    dp.include_router(github_router)

    # Initialize the automated backup system (APScheduler)
    scheduler = setup_backup_scheduler()
    scheduler.start()
    logger.info("Automated Backup Scheduler Started.")

    # Start the GitHub Webhook Server asynchronously
    # (Comment this line out if you don't map port 8080 externally)
    asyncio.create_task(start_webhook_server())

    # Set UI Commands
    await set_bot_commands(bot)

    try:
        logger.info("🚀 CloudHost Bot is now polling for updates...")
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Critical error during bot execution: {e}")
    finally:
        logger.info("Gracefully shutting down services...")
        await docker_manager.close()
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot manually interrupted and stopped.")