import logging
import traceback

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData
from peewee import fn, JOIN

from bot.keyboards.default import get_default_markup
from loader import dp, _
from models import User
from models.person import Person
from models.transactions.Bid import Bid
from models.transactions.Expense import Expanse
from models.transactions.Income import Income
from models.transactions.Transaction import get_default_wallet, Wallet
from models.transactions.WalletPermission import WalletPermission


@dp.message_handler(i18n_text='💰 Кошелёк')
@dp.message_handler(commands='wallet')
async def wallet_handler(message:types.Message,user:User):
    await message.reply('Текущий баланс')
    try:
        query = (Person
                 .select(Person, fn.SUM(Expanse.amount).alias('transaction_amount'),fn.COUNT(Expanse.id).alias('transaction_count'),)
                 .join(Expanse, JOIN.LEFT_OUTER).where(Expanse.wallet==user.wallet)
                 .group_by(Person)
                 .order_by(fn.COUNT(Expanse.id).desc()))
        for person in query:
            text=(_('%s\n*%s трат на сумму %s руб.*') % (person.name, person.transaction_count,person.transaction_amount,))
            await message.answer(text,parse_mode='Markdown')
        wallet=user.wallet

        incomes=Income.select().where(Income.wallet == wallet).order_by(Income.created_at)
        total_sum=0
        total_expense=0
        for tr in incomes:
            text=tr.get_expanses_text()
            total_sum+=tr.amount
            exps_amount = tr.get_expanses_amount()
            total_expense+= exps_amount
            if tr.amount<=exps_amount and 'all' not in message.text:
                continue
            text_ = f'🟢 Поступление *+{tr.amount}*, {tr.created_at.strftime("%d/%m/%Y")}\n\n*ℹ {tr.description}*\nОстаток: *{tr.amount-exps_amount} руб.*\n\n\n{text}'
            await message.reply(text_,parse_mode='Markdown')

        await message.answer(f'*Текущий баланс: {total_sum-total_expense}*\n\nДоход: *{total_sum}*\nРасход: *{total_expense}*',parse_mode='Markdown',reply_markup=get_default_markup(user))
    except:
        err=traceback.format_exc()
        await message.answer(err)
        logging.error(err)

@dp.message_handler(commands='new_wallet')
async def create_wallet(message,user):
    wallet = Wallet.create()
    WalletPermission.create(person=user.person, wallet=wallet)
    await message.answer('кошелек создан')
change_wallet_cb=CallbackData('change_wallet','id')
@dp.message_handler(commands='change_wallet')
async def change_wallet(message:types.Message,user:User,state:FSMContext):
    wallets = Wallet.select().join(WalletPermission).where(WalletPermission.person==user.person)
    kb = types.InlineKeyboardMarkup()
    for wallet in wallets:

        btn=types.InlineKeyboardButton(f'{wallet.id})',callback_data=change_wallet_cb.new(id=wallet.id))
        kb.add(btn)
    await message.answer('выбери кошелек',reply_markup=kb)
@dp.callback_query_handler(change_wallet_cb.filter())
async def change_wallet_handler(query:types.CallbackQuery,user:User,callback_data):
    wallet_id=callback_data['id']
    wallet=Wallet.get_by_id(wallet_id)
    user.wallet=wallet
    user.save()
    await query.message.edit_text(f"{query.message.text}\n {wallet_id} выбран основным")




add_wallet_cb = CallbackData('add_wallet', 'id')


@dp.message_handler(regexp='^/\w+_wallet_user')
async def add_wallet_user(message: types.Message, user: User):
    try:
        wallet=user.wallet
        users_all =set(list( (User
     .select())))
        users_with_permisions =set(list(User.select().join(Person).join(WalletPermission).where(WalletPermission.wallet == wallet)))
        users_excluded=users_all.difference(users_with_permisions)
        if 'add' in message.text:
            users=list(users_excluded)
        else:
            users=users_with_permisions
        kb = types.InlineKeyboardMarkup()
        for user in users:
            is_permision = WalletPermission.get_or_none(WalletPermission.person == user.person,WalletPermission.wallet==wallet)
            perm_txt = '✓' if is_permision else '❌'
            btn = types.InlineKeyboardButton(f'{perm_txt}{user.person.name}', callback_data=add_wallet_cb.new(id=user.id))
            kb.add(btn)
        await message.answer(f'выбери пользователя чтобы {"добавить" if "add" in message.text else "убрать"}', reply_markup=kb)
    except:
        err=traceback.format_exc()
        logging.error(err)
        await message.answer(err)


@dp.callback_query_handler(add_wallet_cb.filter())
async def change_wallet_handler(query: types.CallbackQuery, user: User, callback_data):
    user_id = callback_data['id']
    us = User.get_by_id(user_id)
    wallet=user.wallet
    perms= WalletPermission.get_or_none(person=us.person,wallet=wallet)
    if perms is None:
        WalletPermission.create(person=us.person,wallet=wallet)
        await query.message.edit_text(f"{query.message.text}\n{us.person} добавлен к кошельку",reply_markup=query.message.reply_markup)
    else:
        WalletPermission.delete().where(WalletPermission.person==us.person, WalletPermission.wallet==wallet).execute()
        await query.message.edit_text(f"{query.message.text}\n{us.person} удален из кошелька",reply_markup=query.message.reply_markup)