import datetime
import logging
import traceback

from aiogram.types import Message
from aiogram.utils.callback_data import CallbackData
from peewee import DoesNotExist

from loader import dp
from models import User
from models.transactions.Bid import Bid
from models.transactions.votes.Vote import Vote

from bot.handlers.wallet.bid_utils import bid_voting_cb, bid_to_telegram


@dp.callback_query_handler(bid_voting_cb.filter())
async def create_vote_handler(query: Message, user: User, callback_data):
    try:
        choice=callback_data['choice']
        bid=Bid.get(Bid.id==int(callback_data['bid_id']))
        prev_vote=Vote.get_or_none(Vote.parent == bid , Vote.person==user.person)
        if prev_vote is not None:
            return await query.answer('Вы уже голосовали')
        if bid.closed:
            return await query.answer('Решение уже вынесено')

        Vote.create(person=user.person,choice=choice,parent=bid)
        bid.check_votes()
        kb, text = bid_to_telegram(bid,user.person)
        await query.message.edit_text(text,reply_markup=kb)
    except DoesNotExist:
        await query.message.edit_text('Голосвание удаленно')
    except:
        err = traceback.format_exc()
        logging.error(err)
        await query.message.reply(err)
