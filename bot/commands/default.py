from aiogram.types import BotCommandScopeDefault, BotCommandScopeChat, BotCommand

from loader import _, bot, i18n


def get_default_commands(lang: str = 'en') -> list[BotCommand]:
    commands = [
        BotCommand('/cancel', _('Отменить', locale=lang)),
        BotCommand('/income', _('Новое поступление', locale=lang)),
        BotCommand('/bid', _('Новая заявка на бюджет', locale=lang)),
        BotCommand('/expense', _('Новая трата', locale=lang)),
        BotCommand('/wallet', _('Кошелек', locale=lang)),
        BotCommand('/bids', _('Все заявки на бюджет', locale=lang)),
        BotCommand('/mybids', _('Мои заявки на бюджет', locale=lang)),
        BotCommand('/expenses', _('Мои траты', locale=lang)),
        BotCommand('/incomes', _('Мои поступления', locale=lang)),
        BotCommand('/new_wallet', _('создать кошелек', locale=lang)),
        BotCommand('/change_wallet', _('изменить активный кошелек', locale=lang)),
        BotCommand('/add_wallet_user', _('add user to wallet', locale=lang)),
        BotCommand('/remove_wallet_user', _('remove user from waller', locale=lang)),
        BotCommand('/name', _('change name', locale=lang)),
        BotCommand('/settings', _('open bot settings', locale=lang)),
        BotCommand('/help', _('how it works?', locale=lang)),
    ]

    return commands


async def set_default_commands():
    await bot.set_my_commands(get_default_commands(), scope=BotCommandScopeDefault())

    for lang in i18n.available_locales:
        await bot.set_my_commands(get_default_commands(lang), scope=BotCommandScopeDefault(), language_code=lang)


async def set_user_commands(user_id: int, commands_lang: str):
    await bot.set_my_commands(get_default_commands(commands_lang), scope=BotCommandScopeChat(user_id))
