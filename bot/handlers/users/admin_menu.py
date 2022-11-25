import asyncio
import csv
import logging
import traceback

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, InputFile, InlineKeyboardMarkup, InlineKeyboardButton,CallbackQuery
from aiogram.utils.callback_data import CallbackData

from bot.handlers.chat.chat import desk_st
from loader import dp, bot, config, _
from models import User
from models.person import Role, get_role, Person
from services.users import count_users, get_users


@dp.message_handler(i18n_text='Export users 📁', is_admin=True)
@dp.message_handler(commands=['export_users'], is_admin=True)
async def _export_users(message: Message):
    count = count_users()

    file_path = config.DIR / 'users.csv'
    with open(file_path, 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)

        writer.writerow(['id', 'name', 'username', 'language', 'created_at'])

        for user in get_users():
            writer.writerow([user.id, user.name, user.username, user.language, user.created_at])

    text_file = InputFile(file_path, filename='users.csv')
    await message.answer_document(text_file, caption=_('Total users: {count}').format(count=count))


@dp.message_handler(i18n_text='Count users 👥', is_admin=True)
@dp.message_handler(commands=['count_users'], is_admin=True)
async def _users_count(message: Message):
    count = count_users()

    await message.answer(_('Total users: {count}').format(count=count))

change_role_cb=CallbackData('change_role','id','role')
@dp.message_handler(i18n_text='change role', is_admin=True)
async def change_role(message: Message):
    try:
        users = get_users()
        for user in users:
            try:
                text=f"{user.person.name} tg:'{user.name}' {user.person.role.role}"

                kb=InlineKeyboardMarkup()
                for role in Role.select():
                    if role==user.person.role:continue
                    kb.add(InlineKeyboardButton(f'Поменять роль на {role.role}',callback_data=change_role_cb.new(id=user.id,role=role.role)))
                await message.answer(text,reply_markup=kb)
            except:logging.error(traceback.format_exc())
    except:
        err = traceback.format_exc()
        logging.error(err)
        await message.answer(err)
@dp.callback_query_handler(change_role_cb.filter())
async def change_role_handler(query:CallbackQuery,user:User,callback_data):
    id=callback_data['id']
    role_str=callback_data['role']
    role=get_role(role_str)

    user=User.get_by_id(id)
    person=Person.get(Person.name==user.person.name)
    person.role=role
    person.save()
    user.person=person
    user.is_admin=role_str=='admin'
    user.save()
    await query.message.answer(f'{person.name} role is {role.role}')


@dp.message_handler(i18n_text='Count active users 👥', is_admin=True)
@dp.message_handler(commands=['count_active_users'], is_admin=True)
async def _active_users_count(message: Message):
    users = get_users()

    count = 0
    for user in users:
        try:
            if await bot.send_chat_action(user.id, 'typing'):
                count += 1
        except Exception:
            pass

    await message.answer(_('Active users: {count}').format(count=count))


