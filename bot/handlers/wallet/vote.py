import datetime
import logging
import traceback

from aiogram import types
from aiogram.types import Message
from aiogram.utils.callback_data import CallbackData
from peewee import DoesNotExist, fn

from loader import dp, bot,_
from models import User
from models.person import Person
from models.transactions.Bid import Bid
from models.transactions.votes.VotePermission import VotePermission
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


add_voting_cb = CallbackData('add_voting', 'id')


@dp.message_handler(regexp='^/\w+_voting_user')
@dp.message_handler(i18n_text='Изменить роли')
async def add_voting_user(message: types.Message, user: User):
    try:
        wallet=user.wallet
        users_exc =list( (User
     .select()
     .where(~fn.EXISTS(
          VotePermission.select() ))))
        users_all =list( User.select().join(Person).join(VotePermission).where(VotePermission.wallet == wallet))
        is_removing = 'remove' not in message.text
        if is_removing:
            users=users_exc
        else:
            users=users_all
        kb = types.InlineKeyboardMarkup()
        for user in users:
            is_permision=VotePermission.get_or_none(VotePermission.person==user.person)
            perm_txt='✓' if is_permision else '❌'
            btn = types.InlineKeyboardButton(f'{perm_txt} {user.person.name}', callback_data=add_voting_cb.new(id=user.id))
            kb.add(btn)
        await message.answer(f'выбери пользователя чтобы {"добавить или /remove_voting_user чтобы убрать" if is_removing else "убрать или /add_voting_user чтобы добавить"}', reply_markup=kb)
    except:
        err=traceback.format_exc()
        logging.error(err)
        await message.answer(err)


@dp.callback_query_handler(add_voting_cb.filter())
async def change_voting_handler(query: types.CallbackQuery, user: User, callback_data):
    user_id = callback_data['id']
    us = User.get_by_id(user_id)
    wallet=user.wallet
    perms= VotePermission.get_or_none(person=us.person,wallet=wallet)
    if perms is None:
        VotePermission.create(person=us.person,wallet=wallet)
        await query.message.edit_text(f"{query.message.text}\n{us.person} добавлен к кошельку",reply_markup=query.message.reply_markup)
    else:
        VotePermission.delete().where(VotePermission.person==us.person, VotePermission.wallet==wallet).execute()
        await query.message.edit_text(f"{query.message.text}\n{us.person} удален из кошелька",reply_markup=query.message.reply_markup)