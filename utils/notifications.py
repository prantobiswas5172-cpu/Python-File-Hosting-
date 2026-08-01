from aiogram import Bot
from logs.logger import get_logger

logger = get_logger("bot")

async def notify_user(bot: Bot, user_id: int, message: str):
    """Sends a system alert to the specified user securely."""
    try:
        await bot.send_message(user_id, f"🔔 **Notification**\n\n{message}", parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Failed to send notification to {user_id}: {e}")

async def notify_admins(bot: Bot, message: str, admin_ids: list[int]):
    """Sends critical alerts to all platform administrators."""
    for admin_id in admin_ids:
        try:
            await bot.send_message(admin_id, f"🚨 **ADMIN ALERT**\n\n{message}", parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Failed to send admin alert to {admin_id}: {e}")