import asyncio

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State
from aiogram.types import Message, ReplyKeyboardRemove

from loader import dp, bot
from models import User

desk_st = State('say_all')


@dp.message_handler(i18n_text='Сказать Всем')
async def init_say_all(message: Message):
    await dp.current_state().set_state(desk_st)
    await message.answer('Напишите что отправить всем', reply_markup=ReplyKeyboardRemove())


@dp.message_handler(commands='say', state='*')
@dp.message_handler(state=desk_st)
async def say_all(message: Message, user: User, state: FSMContext):
    users = User.select().where(User.person != None)
    for us in users:
        asyncio.create_task(bot.send_message(us.id, f'{user.person}: {message.text}'))
    await state.reset_state()