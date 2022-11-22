from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State,StatesGroup
from aiogram.types import User

from loader import dp
class TransactionForm(StatesGroup):
    amount=State()
    description=State()

def get_amount_state():return TransactionForm.amount

@dp.message_handler(state=get_amount_state())
async def amount_handler(message:types.Message,user:User,state:FSMContext):
    amount=float(message.text)
    await TransactionForm.next()
    await message.answer('Напиши описание')
    await state.update_data(amount=amount)

@dp.message_handler(state=TransactionForm.description)
async def description_handler(message:types.Message,user:User,state:FSMContext):
    description=(message.text)
    data=await state.get_data()
    fn=data['prev_handler']
    async with state.proxy() as data:
        data['description'] = message.text
    await state.reset_state(False)
    if fn is not None:
        return await fn()