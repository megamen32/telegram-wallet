import asyncio
import logging
import operator
import re
import traceback

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from peewee import fn

from bot.handlers.wallet.bid_utils import bid_to_telegram
from bot.handlers.wallet.remove_entity import create_delete_kb
from bot.states.get_amount import get_amount_state
from loader import dp, bot
from models import User
from models.person import get_role, get_voting_roles, Person
from models.transactions.Expense import Expanse
from models.user import get_voting_persons
from models.transactions.Bid import Bid
from models.transactions.Income import Income
from models.transactions.Transaction import get_default_wallet

bid_cb=CallbackData('choice_bid','bid')
income_cb=CallbackData('choice_income','id','amount')

@dp.message_handler(i18n_text='Заявка 📲')
@dp.message_handler(commands='bid')
async def new_bid_handler(message: Message, user: User,state:FSMContext):
    try:
        amount, description,err = await promt_amount(message, state,prev_handler=lambda :new_bid_handler(message,user,state))
        if err:return
        incomes = Income.select(Income).where(Income.wallet == user.wallet)
        markup = InlineKeyboardMarkup()
        texts = ''
        for i, income in enumerate(incomes):
            totals=income.get_expanses_amount()
            if income.amount - totals < amount: continue
            texts += f'{i})  {income.description} {income.amount}-{totals}={income.amount-totals} id:{income.id} от {income.author.name}\n'
            kb = InlineKeyboardButton(f"{i}) {income.amount-totals} id:{income.id}", callback_data=income_cb.new(id=income.id,amount=amount))
            markup.add(kb)
        if not any(texts):
            texts = f'Не найдено входящих переводов достаточных чтобы создать заявку на сумму {amount}'
            await state.reset_state()
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
        err=False
    except:
        await state.set_state(get_amount_state())
        await state.update_data(prev_handler=prev_handler)
        kb = ReplyKeyboardMarkup()
        kb.add(*(KeyboardButton(text=i) for i in range(1000, 500000, 1000)))
        await message.answer('Введите число', reply_markup=kb)
    return amount, description,err


async def send_all_bid(bid):


    voters=get_voting_persons()
    msgs = []
    for voter in voters:
        kb, text = bid_to_telegram(bid, voter)
        user=User.get_or_none(User.person==voter)

        if user is not None:

            msg=await bot.send_message(user.id,text,reply_markup=kb)
            msgs+=[{'message_id':msg.message_id,'chat_id':msg.chat.id}]
    await dp.storage.set_data(chat=bid.wallet.id,user=bid.id, data={'msgs':msgs})



@dp.callback_query_handler(income_cb.filter())
async def create_bid_handler(query: Message, user: User,callback_data,state):
    try:
        amount = float(callback_data['amount'])
        income_id=int(callback_data['id'])
        data=await state.get_data()
        description=data['description']
        parent_income=Income.get(Income.id==income_id)
        bid = Bid.create(amount=amount, author=user.person, wallet=user.wallet,parent_income=parent_income,description=description)

        await query.message.reply(f'Новое Голосование в размере {amount} с целью {bid.description} начато',reply_markup=create_delete_kb(bid))
        await state.finish()
        await send_all_bid(bid)
    except:
        err = traceback.format_exc()
        logging.error(err)
        await query.message.reply(err)

@dp.message_handler(i18n_text='Все Заявки')
@dp.message_handler(commands='bids')
async def new_expanse_handler(message: Message, user: User):

    try:
        bids=Bid.select().where(Bid.wallet==user.wallet)
        markup = InlineKeyboardMarkup()
        texts=''
        for i,bid in enumerate(bids):
            bid.check_votes()
            totals = 0
            expanses = list(
                Expanse.select(Expanse).where(Expanse.parent_bid == bid))
            if any(expanses) and expanses[0].id is not None:
                totals = sum(map(operator.attrgetter('amount'), expanses))
            texts += f'\n{i}) {bid.author.name} {bid.amount}-{totals}={bid.amount-totals} описание: {bid.description} | {"уже закрыта" if bid.closed else "еще открыта"} счет:{bid.calc_aprove_rating()}'
            spendings=bid.amount
            for tr2 in expanses:
                spendings -= tr2.amount
                texts += f'\n\t\tТрата -{tr2.amount} от"{tr2.author.name}" {tr2.created_at.strftime("%d/%m/%Y, %H:%M")} Б-с:{spendings} {tr2.description} '
        if not any(texts):
            texts=f'В кошельке {user.wallet.id} нет заявок'
        await message.reply(texts)
    except:
        err = traceback.format_exc()
        logging.error(err)
        await message.reply(err)