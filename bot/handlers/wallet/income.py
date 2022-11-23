import logging
import re
import traceback

from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from bot.handlers.wallet.bid import promt_amount
from bot.handlers.wallet.remove_entity import create_delete_kb
from loader import dp
from models import User
from models.transactions.Income import Income
from models.transactions.Transaction import get_default_wallet

@dp.message_handler(i18n_text='Поступление ✅')
@dp.message_handler(commands='income')
async def new_income_handler(message:Message,user:User,state:FSMContext):
    try:
        amount, description,err = await promt_amount(message, state,prev_handler=lambda :new_income_handler(message,user,state))
        if err: return
        income=Income.create(amount=amount,author=user.person,wallet=get_default_wallet(),description=description)
        await message.reply(f'Новое Поступление в размере {amount} начислено. Описание: {income.description}',reply_markup=create_delete_kb(income))
        await state.reset_state(True)
    except:
        err = traceback.format_exc()
        await message.reply(err)
        logging.error(err)
