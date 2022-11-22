import asyncio
import logging
import re
import traceback

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from bot.handlers.wallet.bid_utils import bid_to_telegram
from bot.states.get_amount import get_amount_state
from loader import dp, bot
from models import User
from models.person import get_role, get_voting_roles, Person
from models.user import get_voting_persons
from models.transactions.Bid import Bid
from models.transactions.Income import Income
from models.transactions.Transaction import get_default_wallet

bid_cb=CallbackData('choice_bid','bid')
income_cb=CallbackData('choice_income','id','amount')


@dp.message_handler(commands='bid')
async def new_bid_handler(message: Message, user: User,state:FSMContext):
    try:
        amount, description,err = await promt_amount(message, state,prev_handler=lambda :new_bid_handler(message,user,state))
        if err:return
        bids = Income.select()
        markup = InlineKeyboardMarkup()
        texts = ''
        for i, income in enumerate(bids):
            texts += f'{i}{income.author.name}{income.description} {income.amount} id:{income.id}\n'
            kb = InlineKeyboardButton(f"{i} {income.amount} id:{income.id}", callback_data=income_cb.new(id=income.id,amount=amount))
            markup.add(kb)
        await message.reply(texts, reply_markup=markup)
    except:
        err = traceback.format_exc()
        logging.error(err)
        await message.reply(err)


async def promt_amount(message, state,prev_handler=None):
    err = True
    amount=0
    description=''
    try:
        data = await state.get_data()
        amount = data['amount'] or float(re.findall(r'(\d+)', message.text)[0])
        description=data['description']
        err = False
    except:
        await state.set_state(get_amount_state())
        await state.update_data(prev_handler=prev_handler)
        kb = ReplyKeyboardMarkup()
        kb.add(*(KeyboardButton(text=i) for i in range(1000, 500000, 1000)))
        await message.answer('Введите число', reply_markup=kb)
    return amount, description,err


async def send_all_bid(bid):


    voters=get_voting_persons()
    for voter in voters:
        kb, text = bid_to_telegram(bid, voter)
        user=User.get_or_none(User.person==voter)
        if user is not None:
            asyncio.create_task( bot.send_message(user.id,text,reply_markup=kb))


@dp.callback_query_handler(income_cb.filter())
async def create_bid_handler(query: Message, user: User,callback_data,state):
    try:
        amount = float(callback_data['amount'])
        income_id=int(callback_data['id'])
        data=await state.get_data()
        description=data['description']
        parent_income=Income.get(Income.id==income_id)
        bid = Bid.create(amount=amount, author=user.person, wallet=get_default_wallet(),parent_income=parent_income,description=description)
        await query.message.reply(f'Новое Голосование в размере {amount} с целью {bid.description} начато')
        await state.finish()
        await send_all_bid(bid)
    except:
        err = traceback.format_exc()
        logging.error(err)
        await query.message.reply(err)


@dp.message_handler(commands='bids')
async def new_expanse_handler(message: Message, user: User):

    try:
        bids=Bid.select()
        markup = InlineKeyboardMarkup()
        texts=''
        for i,bid in enumerate(bids):
            bid.check_votes()
            texts += f'{i}) {bid.author.name} {bid.amount} id:{bid.id} {bid.description} finish:{bid.approved} rating:{bid.calc_aprove_rating()}\n'

        await message.reply(texts)
    except:
        err = traceback.format_exc()
        logging.error(err)
        await message.reply(err)