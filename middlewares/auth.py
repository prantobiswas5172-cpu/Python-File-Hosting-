from aiogram import BaseMiddleware
from aiogram.types import Message
from database.db import async_session
from database.models import User
from sqlalchemy import select

class AuthMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: dict):
        async with async_session() as session:
            user = await session.scalar(select(User).where(User.telegram_id == event.from_user.id))
            if not user:
                user = User(telegram_id=event.from_user.id, username=event.from_user.username)
                session.add(user)
                await session.commit()
            
            if user.is_banned:
                await event.answer("🚫 You are banned from using this service.")
                return
            
            data['db_user'] = user
            data['session'] = session
            return await handler(event, data)