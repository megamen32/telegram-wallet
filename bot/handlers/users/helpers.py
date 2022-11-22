import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message

from bot.keyboards.default import get_default_markup
from loader import dp, _
from models import User

# You can use state '*' if you need to handle all states
@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('Cancelled.', reply_markup=types.ReplyKeyboardRemove())
@dp.message_handler(state='*')
async def _default_menu(message: Message, user: User,state:FSMContext):
    cur_state=await state.get_state()
    await message.answer(_('Я не понимаю чего ты от меня хочешь'), reply_markup=get_default_markup(user))
    if cur_state is not None:
        return await message.answer(_('нажми /cancel чтобы отменить текущее действие'), reply_markup=get_default_markup(user))

