from calendar import c
from aiogram.filters import Filter
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Bot, types

from db.orm_query import orm_get_admins

#Этот скрипт в доработке не нуждается

class ChatTypeFilter(Filter):
    def __init__(self, chat_types: list[str]) -> None:
        self.chat_types = chat_types

    async def __call__(self, message: types.Message) -> bool:
        return message.chat.type in self.chat_types

class IsAdmin(Filter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: types.Message, bot: Bot, session: AsyncSession) -> bool:
        return message.from_user.username in await orm_get_admins(session)
