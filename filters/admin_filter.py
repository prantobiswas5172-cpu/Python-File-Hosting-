from aiogram.filters import BaseFilter
from aiogram.types import Message
from config import settings

class IsAdminFilter(BaseFilter):
    """
    Filter to check if the user is in the ADMIN_IDS list.
    """
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in settings.ADMIN_IDS