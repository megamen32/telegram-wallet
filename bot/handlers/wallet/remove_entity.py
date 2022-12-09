import logging
import traceback

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from loader import dp
from models import User
from models.transactions.Bid import Bid
from models.transactions.Expense import Expanse
from models.transactions.Income import Income
from models.transactions.votes.Vote import Vote

del_cb=CallbackData('remove', 'id', 'classname')


@dp.callback_query_handler(del_cb.filter())
async def del_expanse_handler(query: types.CallbackQuery,user:User, callback_data: dict,state:FSMContext):
    try:
        id=int(callback_data['id'])
        classname=(callback_data['classname'])
        eval(f'{classname}.get_by_id(id).delete_instance(recursive=True)')
        await query.message.edit_text(f'Удалено!\n\n{query.message.text}',reply_markup=InlineKeyboardMarkup())
    except:
        err = traceback.format_exc()
        logging.error(err)
        await query.answer(err)


def create_delete_kb(expance):
    kb = InlineKeyboardMarkup()
    del_btn = InlineKeyboardButton('Удалить', callback_data=del_cb.new(id=expance.id, classname=type(expance).__name__))
    kb.add(del_btn)
    return kb
