from aiogram.dispatcher.filters.builtin import CommandStart, CommandHelp
from aiogram.types import Message

from bot.commands import get_admin_commands, get_default_commands
from bot.commands import set_admin_commands
from bot.keyboards.inline import get_language_inline_markup
from bot.states.registation import get_registration_state
from loader import dp, _
from models import User
from models.person import Person, get_role


@dp.message_handler(CommandStart())
async def _start(message: Message, user: User):
    if user.is_admin:
        await set_admin_commands(user.id, user.language)
    if user.person is None:
        await ask_register(message)
    else:
        await message.reply(_(f"Hello {user.person.name}"))

@dp.message_handler(commands='name')
async def ask_register(message):
    text = _('Enter your nmae: Lastname Name Fathername 🆘')
    await dp.current_state().set_state(get_registration_state())
    await message.reply(text)


@dp.message_handler(i18n_text='Help 🆘')
@dp.message_handler(CommandHelp())
async def _help(message: Message, user: User):
    if user.person is not None:
        commands = get_admin_commands(user.language) if user.is_admin else get_default_commands(user.language)
    else:
        return await _start(message,user)
    text = _('Help 🆘') + '\n\n'
    for command in commands:
        text += f'{command.command} - {command.description}\n'

    await message.answer(text)





