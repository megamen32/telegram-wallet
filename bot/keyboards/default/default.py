from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove

from loader import _


def get_default_markup(user):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)

   # markup.add(_('Help 🆘'), _('Settings 🛠'))
    markup.add(_('Заявка 📲'), _('Трата 💸'),_('Поступление ✅ '))
    markup.add(_('Заявки'),_('Последние Траты'),_('Кошелек 💱'))
    markup.add(_('Мои Заявки'),_('Поступления'))

    if user.is_admin:
        markup.add(_('change role'))
        markup.add(_('Count active users 👥'))

    if len(markup.keyboard) < 1:
        return ReplyKeyboardRemove()

    return markup
