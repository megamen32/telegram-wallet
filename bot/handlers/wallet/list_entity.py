import asyncio
import logging
import traceback
from datetime import datetime, timedelta

from aiogram.types import Message, InlineKeyboardMarkup
from peewee import DoesNotExist

from bot.handlers.wallet.bid_utils import bid_to_telegram
from bot.handlers.wallet.remove_entity import create_delete_kb
from loader import dp
from models import User
from models.transactions.Bid import Bid
from models.transactions.Expense import Expanse
from models.transactions.Income import Income
from models.transactions.votes.Vote import Vote


@dp.message_handler(i18n_text='Мои заявки')
@dp.message_handler(commands='mybids')
async def list_bids_handler(message:Message,user:User):
    try:
        expanses=Bid.select().where(Bid.author==user.person,Bid.wallet==user.wallet).order_by(Bid.created_at)
        for i, bid in  enumerate(expanses):
            spendings=Expanse.select().where(Expanse.parent_bid == bid)
            if any(spendings):
                kb = InlineKeyboardMarkup()
            else:

                kb= create_delete_kb(bid)
            texts=bid.get_expenses_text()

            await message.answer(texts,reply_markup=kb,parse_mode='Markdown')
        if not any(expanses): await message.answer('У вас нет заявок')

    except:
        err = traceback.format_exc()
        logging.error(err)
        await message.answer(err)
@dp.message_handler(i18n_text='Мои поступления')
@dp.message_handler(commands='incomes')
async def list_incomes_handler(message:Message,user:User):
    try:
        expanses=Income.select().where(Income.author==user.person,Income.wallet==user.wallet).order_by(Income.created_at)
        for exp in  expanses:
            spendigs =  Expanse.select().join(Bid).where(Bid.parent_income==exp)
            if any(spendigs):
                kb=InlineKeyboardMarkup()
            else:
                kb= create_delete_kb(exp)
            text=f'{exp.created_at.strftime("%d/%m/%Y, %H:%M")}\n\n*+{exp.amount}* | {exp.description} '
            await message.answer(text,reply_markup=kb,parse_mode='Markdown')
        if not any(expanses):await message.answer('У вас нет поступлений')
    except DoesNotExist:
        await message.answer('У вас нет поступлений')
    except:
        err = traceback.format_exc()
        logging.error(err)
        await message.answer(err)
@dp.message_handler(commands='votes')
@dp.message_handler(i18n_text='📢 Голосования')
async def list_votes(message:Message,user:User):
    try:
        bids=Bid.select().where(Bid.closed==False,Bid.wallet==user.wallet).order_by(Bid.created_at)
        for bid in bids:
            kb, text = bid_to_telegram(bid, user.person)
            asyncio.create_task(message.answer( text, reply_markup=kb))
        if not any(bids): await message.answer('Нет активных голосований')
    except DoesNotExist:
        await message.answer('Нет активных голосований')
    except:
        err = traceback.format_exc()
        logging.error(err)
        await message.answer(err)