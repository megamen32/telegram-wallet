from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message
from aiogram.dispatcher import FSMContext
from bot.keyboards.inline import get_language_inline_markup
from loader import dp,_
from models import User
from models.person import Person, get_role

def get_registration_state()->State:
    state=State('enter_name',group_name='register')
    return state



@dp.message_handler(state=get_registration_state(),regexp='^[а-яА-Я]+ [а-яА-Я]+ [а-яА-Я]+$')
async def name_handler(message: Message, user: User,state:FSMContext):
    name=message.text
    role='admin' if user.is_admin else 'user'
    user.person=Person.create(name=name,role=get_role(role))
    user.save()
    await state.finish()
    text = _('Hi {full_name}!\n'
             'Choose your language').format(full_name=name)
    await message.answer(text, reply_markup=get_language_inline_markup())
@dp.message_handler(state=get_registration_state())
async def name_handler(message: Message, user: User):
    text = _(f'Введено неправильное имя, пожалуйста введи Фамилию Имя Очество')
    await message.answer(text)