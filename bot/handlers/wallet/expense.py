import logging
import traceback

from aiogram import types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from bot.handlers.wallet.bid import bid_cb
from loader import dp
from models import User
from models.transactions.Bid import Bid
from models.transactions.Expense import Expanse
from models.transactions.Transaction import get_default_wallet

@dp.message_handler(i18n_text='Трата 💸')
@dp.message_handler(commands='expense')
async def new_expanse_handler(message: Message, user: User):

    try:
        bids=Bid.select().where(Bid.author == user.person, Bid.closed == True,Bid.was_used==False)
        markup = InlineKeyboardMarkup()
        texts=''
        for i,bid in enumerate(bids):
            was_used=Expanse.get_or_none(Expanse.parent_bid==bid)
            if was_used:
                bid.was_used=True
                continue
            texts += f'{i}) {bid.author.name} {bid.amount} id:{bid.id} {bid.description}\n'
            kb=InlineKeyboardButton(f"{i} {bid.amount} id:{bid.id}", callback_data=bid_cb.new(bid=bid.id))
            markup.add(kb)
        if not any(texts):
            texts='Одобренные Заявки на траты не найдены. Сначала надо создать заявку /bid'
        await message.reply(texts,reply_markup=markup)
    except:
        err = traceback.format_exc()
        logging.error(err)
        await message.reply(err)


@dp.callback_query_handler(bid_cb.filter())
async def create_expanse_handler(query: types.CallbackQuery,user:User, callback_data: dict):
    bid_id=int(callback_data['bid'])

    bid=Bid.get(Bid.id==bid_id)
    amount=bid.amount
    if bid.closed:
        if not bid.approved: await query.message.reply(f'Заявка уже отклонена')
        expance=Expanse.create(parent_bid=bid,amount=amount,author=user.person,wallet=get_default_wallet(),description=bid.description)
        await query.message.reply(f'Новая трата в размере {amount}, создана! ')
    else:
        await query.message.reply(f'Заявка еще не одобрена!')
