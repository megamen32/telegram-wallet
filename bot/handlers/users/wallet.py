import re

from aiogram import types
from aiogram.utils.callback_data import CallbackData
from peewee import fn
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from loader import dp,_
from models import User
from models.transactions.Bid import Bid
from models.transactions.Expense import Expanse
from models.transactions.Income import Income
from models.transactions.Transaction import Transaction


@dp.message_handler(commands='wallet')
async def ask_register(message):
    query = Transaction.select(fn.SUM(Transaction.value).over(order_by=[Transaction.id]).alias('amount'))
    text = _(f'Current wallet balance {query}')
    await message.reply(text)
    for tr in Transaction.select().order_by(Transaction.created_at):
        await message.reply(tr)
@dp.message_handler(commands='income')
async def new_income_handler(message:Message,user:User):
    amount=float(re.findall(r'(\d+)',message.text)[0])
    income=Income.create(amount=amount,author=user.person)
    await message.reply(f'Новое Поступление в размере {amount} начисленно')


@dp.message_handler(commands='bid')
async def new_income_handler(message: Message, user: User):
    amount = float(re.findall(r'(\d+)', message.text)[0])
    bid = Bid.create(amount=amount, author=user.person)
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
