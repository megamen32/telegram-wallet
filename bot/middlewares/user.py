import asyncio

from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Message, CallbackQuery, InlineQuery

from data.config import TG_PASSWORD
from loader import _,dp
from services.users import get_or_create_user, get_user


class UsersMiddleware(BaseMiddleware):
    @staticmethod
    async def on_process_message(message: Message, data: dict[str]):
        if 'channel_post' in message or message.chat.type != 'private':
            raise CancelHandler()

        await message.answer_chat_action('typing')

        user = message.from_user
        u=get_user(user.id)
        if u is None and f'/start {TG_PASSWORD}' not in message.text:
            asyncio.create_task( message.reply(_(f"Нет доступа")))
            raise CancelHandler()
        data['user'] = get_or_create_user(user.id, user.full_name, user.username, user.language_code)
        if '/cancel' in message.text:
            from bot.handlers.users.helpers import cancel_handler
            await cancel_handler(message,state=data['state'])
            raise CancelHandler()


    @staticmethod
    async def on_process_callback_query(callback_query: CallbackQuery, data: dict[str]):
        user = callback_query.from_user

        data['user'] = get_or_create_user(user.id, user.full_name, user.username, user.language_code)

    @staticmethod
    async def on_process_inline_query(inline_query: InlineQuery, data: dict[str]):
        user = inline_query.from_user

        data['user'] = get_or_create_user(user.id, user.full_name, user.username, user.language_code)
