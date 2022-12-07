import datetime
import logging
import traceback

from aiogram.types import Message
from aiogram.utils.callback_data import CallbackData
from peewee import DoesNotExist

from loader import dp, bot
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
        try:
            storage_data = await dp.storage.get_data(chat=bid.wallet.id, user=bid.id)
            msgs_ids = storage_data['msgs']
            for val in msgs_ids:
                chat_id=val['chat_id']
                msg_id=val['message_id']
                if msg_id!=query.message.message_id:
                    us=User.get_or_none(User.id==chat_id)
                    if us is not None:
                        kb,text=bid_to_telegram(bid,us.person)
                    else:
                        kb=None
                    await bot.edit_message_text(text,chat_id=chat_id,message_id=msg_id,reply_markup=kb)
        except:
            logging.error(traceback.format_exc())
    except DoesNotExist:
        await query.message.edit_text('Голосование удалено!')
    except:
        err = traceback.format_exc()
        logging.error(err)
        await query.message.reply(err)
