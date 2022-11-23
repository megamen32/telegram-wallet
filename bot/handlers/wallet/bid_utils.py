import traceback

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from models.transactions.votes.Vote import Vote

bid_voting_cb=CallbackData('bid_voting','bid_id','choice')
def bid_to_telegram(bid,person=None):
    kb = InlineKeyboardMarkup()
    votes = list(Vote.select().where(Vote.parent == bid))
    text = f'Новая заявка на бюджет в размере {bid.amount} от {bid.author.name} со средств {bid.parent_income.description} {bid.parent_income.amount}\n\t\tописание: {bid.description}'
    for v in votes:
        text += f'\n{v.person.name}: {v.choice}'
    y = InlineKeyboardButton('Yes', callback_data=bid_voting_cb.new(bid_id=bid.id, choice=1))
    n = InlineKeyboardButton('No', callback_data=bid_voting_cb.new(bid_id=bid.id, choice=0))
    made_vote=False
    try:
        made_vote = Vote.get_or_none(Vote.parent == bid , Vote.person == person) is not None
    except:
        traceback.print_exc()
    if not made_vote:
        kb.add(y, n)
    return kb, text
