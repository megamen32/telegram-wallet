import logging
import operator
import traceback
from datetime import datetime, timedelta

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from peewee import fn

from bot.handlers.wallet.bid import bid_cb, promt_amount
from bot.handlers.wallet.remove_entity import create_delete_kb
from loader import dp
from models import User
from models.transactions.Bid import Bid
from models.transactions.Expense import Expanse
from models.transactions.Transaction import get_default_wallet

@dp.message_handler(i18n_text='💸 Трата')
@dp.message_handler(commands='expense')
async def new_expanse_handler(message: Message, user: User,state:FSMContext):

    try:
        bids=Bid.select(Bid).where(Bid.wallet==user.wallet,Bid.author == user.person)
        markup = InlineKeyboardMarkup()
        texts=''
        for i,bid in enumerate(bids):
            totals=bid.get_expenses_amount()
            if bid.was_used:continue
            texts += f'{i}) {bid.author.name} {bid.amount}-{totals}={bid.amount-totals} id:{bid.id} {bid.description}\n'
            kb=InlineKeyboardButton(f"{i} {bid.amount} id:{bid.id}", callback_data=bid_cb.new(bid=bid.id))
            markup.add(kb)

        if not any(texts):
            texts='Сначала создай заявку на трату /bid'
            return await message.reply(texts)
        amount, description, err = await promt_amount(message, state,
                                                      prev_handler=lambda: new_expanse_handler(message, user, state))
        if err: return
        await state.update_data(amount=amount,description=description)
        await message.reply(texts,reply_markup=markup)
    except:
        err = traceback.format_exc()
        logging.error(err)
        await message.reply(err)


@dp.callback_query_handler(bid_cb.filter())
async def create_expanse_handler(query: types.CallbackQuery,user:User, callback_data: dict,state:FSMContext):
    bid_id=int(callback_data['bid'])
    data=await dp.storage.get_data(chat=user.id)
    amount=data['amount']
    description=data['description']
    bid=Bid.get(Bid.id==bid_id)

    if bid.closed:
        if not bid.approved: await query.message.reply(f'Заявка уже отклонена.')
        expance=Expanse.create(parent_bid=bid,amount=amount,author=user.person,wallet=user.wallet,description=description)
        kb =  create_delete_kb(expance)
        await query.message.reply(f'*Трата на сумму {amount} руб. создана!*',reply_markup=kb,parse_mode='Markdown')
        await state.finish()
    else:
        await query.message.reply(f'Заявка еще не одобрена!')


@dp.message_handler(i18n_text='Мои траты')
@dp.message_handler(commands='expenses')
async def spendigs(message:Message,user:User):
    try:
        expanses=Expanse.select().join(Bid).where(Bid.author==user.person,Bid.wallet==user.wallet).order_by(Expanse.created_at)
        for exp in  expanses:
            kb= create_delete_kb(exp)
            text=f'💸*– {exp.amount}*, {exp.description} {exp.created_at.strftime("%d/%m/%Y, %H:%M")}\n\t\tОплачено с заявки ➡ {exp.parent_bid.amount}, {exp.parent_bid.description}'
            await message.answer(text,reply_markup=kb,parse_mode='Markdown')
        if not any(expanses): await message.answer('Ничего не потрачено.. пока что')
    except:
        err = traceback.format_exc()
        logging.error(err)
        await message.answer(err)

