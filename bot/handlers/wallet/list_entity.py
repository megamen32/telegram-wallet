import logging
import traceback
from datetime import datetime, timedelta

from aiogram.types import Message, InlineKeyboardMarkup

from bot.handlers.wallet.remove_entity import create_delete_kb
from loader import dp
from models import User
from models.transactions.Bid import Bid
from models.transactions.Expense import Expanse
from models.transactions.Income import Income
from models.transactions.votes.Vote import Vote


@dp.message_handler(i18n_text='Мои Заявки')
@dp.message_handler(commands='mybids')
async def list_bids_handler(message:Message,user:User):
    try:
        expanses=Bid.select().where(Bid.author==user.person).order_by(Bid.created_at)
        for exp in  expanses:
            if exp.closed:
                kb = InlineKeyboardMarkup()
            else:

                kb= create_delete_kb(exp)
            text=f'{exp.amount} {exp.description} {exp.created_at}\n\t\tПоступление->{exp.parent_income.amount} {exp.parent_income.description}'
            await message.answer(text,reply_markup=kb)
    except:
        err = traceback.format_exc()
        logging.error(err)
        await message.answer(err)
@dp.message_handler(i18n_text='Поступления')
@dp.message_handler(commands='incomes')
async def list_incomes_handler(message:Message,user:User):
    try:
        expanses=Income.select().where(Income.author==user.person).order_by(Income.created_at)
        for exp in  expanses:
            spendigs =  Expanse.select().join(Bid).where(Bid.parent_income==exp)
            if any(spendigs):
                kb=InlineKeyboardMarkup()
            else:
                kb= create_delete_kb(exp)
            text=f'{exp.amount} {exp.description} {exp.created_at}\n\t\t'
            await message.answer(text,reply_markup=kb)
    except:
        err = traceback.format_exc()
        logging.error(err)
        await message.answer(err)