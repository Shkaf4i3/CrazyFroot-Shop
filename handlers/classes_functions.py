from cachetools import TTLCache
from os import getenv
from dotenv import load_dotenv
from typing import Any, Awaitable, Callable, Dict

from aiogram.filters import Filter
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram import BaseMiddleware
import reply as kb


load_dotenv()


# Проверка пользователя на наличие в списке admin_id для доступа к админским командам и запросам
class IsAdmin(Filter):
    @staticmethod
    async def __call__(message: Message):
        return str(message.from_user.id) in getenv('admin_id')


# Классы для работы через FSM
class Add_sc(StatesGroup):
    login = State()
    password = State()

class Add_eg(StatesGroup):
    login = State()
    password = State()

class Balance_state(StatesGroup):
    amount = State()


# Класс для проверки наличия подписки пользователя на телеграм канал
class CheckSubscribe(BaseMiddleware):
    async def __call__(self,
                       handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
                       event: Message,
                       data: Dict[str, Any]) -> Any:
        chat_members = await event.bot.get_chat_member(
            chat_id=getenv('channel_id'),
            user_id=event.from_user.id)

        if chat_members.status == 'left':
            await event.answer('Для продолжения работы подпишитесь на канал 💚',
                           reply_markup=kb.url_channel())
        else:
            return await handler(event, data)


# Класс для анти-спам системы (кд сообщений - 1 секунда)
class AntiFloodMiddleware(BaseMiddleware):

    def __init__(self, time_limit: int=1) -> None:
        self.limit = TTLCache(maxsize=10_000, ttl=time_limit)

    async def __call__(self,
                       handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
                       event: Message,
                       data: Dict[str, Any]) -> Any:
        if event.chat.id in self.limit:
            return
        else:
            self.limit[event.chat.id] = None
        return await handler(event, data)
