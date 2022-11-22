import logging
import traceback

from aiogram import types
from peewee import fn, JOIN
from loader import dp, _
from models.person import Person
from models.transactions.Bid import Bid
from models.transactions.Expense import Expanse
from models.transactions.Income import Income
from models.transactions.Transaction import get_default_wallet


@dp.message_handler(commands='wallet')
async def ask_register(message:types.Message):
    await message.reply('Текуший баланс')
    try:
        query = (Person
                 .select(Person, fn.SUM(Expanse.amount).alias('transaction_amount'),fn.COUNT(Expanse.id).alias('transaction_count'),)
                 .join(Expanse, JOIN.LEFT_OUTER)
                 .group_by(Person)
                 .order_by(fn.COUNT(Expanse.id).desc()))
        for person in query:
            text=(_('%s -- %s трат, на сумму %s') % (person.name, person.transaction_count,person.transaction_amount,))
            await message.answer(text)
        wallet=get_default_wallet()

        trs=Income.select().where(Income.wallet==wallet).order_by(Income.created_at)

        for tr in trs:
            exp = Expanse.select().join(Bid).where(Bid.parent_income==tr).order_by(Expanse.created_at)
            exp=list(exp)
            sum=tr.amount
            text=''
            for tr2 in exp:
                sum-=tr2.amount
                text += f'\n\t\tБ-с:{sum} Трата -{tr2.amount} от:"{tr2.author.name}" {tr2.created_at} {tr2.description}'
            await message.reply(f'Поступление {tr.amount} {tr.description} {tr.created_at} Осталось:{sum}{text}')

    except:
        err=traceback.format_exc()
        await message.answer(err)
        logging.error(err)


