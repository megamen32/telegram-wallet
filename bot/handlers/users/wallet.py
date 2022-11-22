import logging
import re
import traceback

from aiogram import types
from aiogram.utils.callback_data import CallbackData
from peewee import fn, JOIN
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from loader import dp,_
from models import User
from models.person import Person
from models.transactions.Bid import Bid
from models.transactions.Expense import Expanse
from models.transactions.Income import Income
from models.transactions.Transaction import Transaction,get_default_wallet



@dp.message_handler(commands='wallet')
async def ask_register(message:types.Message):
    await message.reply('Текуший баланс')
    try:
        #query = Transaction.select(Transaction,fn.SUM(Transaction.amount).alias('balance')).join()
        query = (Person
                 .select(Person, fn.COUNT(Transaction.id).alias('transaction_amount'))
                 .join(Transaction, JOIN.LEFT_OUTER)
                 .group_by(Person)
                 .order_by(fn.COUNT(Transaction.id).desc()))
        for person in query:
            text=(_('%s -- %s tweets') % (person.name, person.transaction_amount))
            await message.answer(text)
        wallet=get_default_wallet()
        trs=Income.select().order_by(Income.created_at)


        for tr in trs:
            await message.reply(f'{tr.amount} {tr.description} {tr.created_at}')
    except:
        err=traceback.format_exc()
        await message.answer(err)
        logging.error(err)
@dp.message_handler(commands='income')
async def new_income_handler(message:Message,user:User):
    try:
        amount=float(re.findall(r'(\d+)',message.text)[0])
        income=Income.create(amount=amount,author=user.person,wallet=get_default_wallet())
        await message.reply(f'Новое Поступление в размере {amount} начисленно')
    except:
        err = traceback.format_exc()
        await message.reply(err)
        logging.error(err)

@dp.message_handler(commands='bid')
async def new_income_handler(message: Message, user: User):
    amount = float(re.findall(r'(\d+)', message.text)[0])
    bid = Bid.create(amount=amount, author=user.person,wallet=get_default_wallet())
    await message.reply(f'Новое Голосование в размере {amount} с целью {bid.description} начато')

bid_cb=CallbackData('choice_bid','bid','amount')
@dp.message_handler(commands='expense')
async def new_expanse_handler(message: Message, user: User):
    amount = float(re.findall(r'(\d+)', message.text)[0])

    bids=Bid.select(Bid.author==user)
    markup = InlineKeyboardMarkup()
    for i,bid in enumerate(bids):
        kb=InlineKeyboardButton(f'{i}{bid}',callback_data=bid_cb.new(bid=bid.id,amount=amount))
        markup.add(kb)
    await message.reply('',reply_markup=markup)

async def bid_filter_handler(query: types.CallbackQuery,user:User, callback_data: dict):
    bid_id=callback_data['bid']
    amount=callback_data['amount']
    bid=Bid.select(Bid.id==bid_id).get()
    expance=Expanse.create(parent_bid=bid,amount=amount,author=user.person)
    await query.message.reply(f'Новая трата в размере {amount}, создана! ')
