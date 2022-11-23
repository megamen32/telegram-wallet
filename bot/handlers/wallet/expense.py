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

@dp.message_handler(i18n_text='Трата 💸')
@dp.message_handler(commands='expense')
async def new_expanse_handler(message: Message, user: User,state:FSMContext):

    try:
        bids=Bid.select().where(Bid.author == user.person, Bid.closed == True,Bid.was_used==False)
        markup = InlineKeyboardMarkup()
        texts=''
        for i,bid in enumerate(bids):
            expanses=list(Expanse.select(Expanse,fn.SUM(Expanse.amount).alias('sum')).where(Expanse.parent_bid==bid))
            totals=0
            if  any(expanses) and expanses[0].id is not None:
                totals=sum(map(operator.attrgetter('sum'),expanses))
                if totals>=bid.amount:
                    bid.was_used=True
                    bid.save()
                    continue
            texts += f'{i}) {bid.author.name} {bid.amount}-{totals}={bid.amount-totals} id:{bid.id} {bid.description}\n'
            kb=InlineKeyboardButton(f"{i} {bid.amount} id:{bid.id}", callback_data=bid_cb.new(bid=bid.id))
            markup.add(kb)

        if not any(texts):
            texts='Одобренные Заявки на траты не найдены. Сначала надо создать заявку /bid'
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
    data=await state.get_data()
    amount=data['amount']
    description=data['description']
    bid=Bid.get(Bid.id==bid_id)

    if bid.closed:
        if not bid.approved: await query.message.reply(f'Заявка уже отклонена')
        expance=Expanse.create(parent_bid=bid,amount=amount,author=user.person,wallet=get_default_wallet(),description=description)
        kb =  create_delete_kb(expance)
        await query.message.reply(f'Новая трата в размере {amount}, создана! ',reply_markup=kb)
        await state.finish()
    else:
        await query.message.reply(f'Заявка еще не одобрена!')


@dp.message_handler(i18n_text='Мои Последние Траты')
@dp.message_handler(commands='expenses')
async def spendigs(message:Message,user:User):
    try:
        expanses=Expanse.select().where(Expanse.created_at>(datetime.now() - timedelta(days=1))).join(Bid).where(Bid.author==user.person).order_by(Expanse.created_at)
        for exp in  expanses:
            kb= create_delete_kb(exp)
            text=f'{exp.amount} {exp.description} {exp.created_at}\n\t\tзаявка->{exp.parent_bid.amount} {exp.parent_bid.description}'
            await message.answer(text,reply_markup=kb)
    except:
        err = traceback.format_exc()
        logging.error(err)
        await message.answer(err)

