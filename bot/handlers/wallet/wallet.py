import logging
import traceback

from aiogram import types
from peewee import fn, JOIN

from bot.keyboards.default import get_default_markup
from loader import dp, _
from models import User
from models.person import Person
from models.transactions.Bid import Bid
from models.transactions.Expense import Expanse
from models.transactions.Income import Income
from models.transactions.Transaction import get_default_wallet

@dp.message_handler(i18n_text='Кошелек 💱')
@dp.message_handler(commands='wallet')
async def wallet_handler(message:types.Message,user:User):
    await message.reply('Текущий баланс')
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
        total_sum=0
        total_expense=0
        for tr in trs:
            exp = Expanse.select().join(Bid).where(Bid.parent_income==tr).order_by(Expanse.created_at)
            exp=list(exp)
            sum=tr.amount
            total_sum += sum
            text=''
            for tr2 in exp:
                total_expense+=tr2.amount
                sum-=tr2.amount
                text += f'\n\t\tТрата -{tr2.amount} от:"{tr2.author.name}" {tr2.created_at} Б-с:{sum} {tr2.description} '
            await message.reply(f'Поступление {tr.amount} {tr.description} {tr.created_at} Осталось:{sum}{text}')

        await message.answer(f'Доход {total_sum} Расход {total_expense} Итоговый баланс {total_sum-total_expense}',reply_markup=get_default_markup(user))
    except:
        err=traceback.format_exc()
        await message.answer(err)
        logging.error(err)


