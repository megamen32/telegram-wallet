import traceback

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from models.transactions.votes.Vote import Vote
from models.user import get_voting_persons

bid_voting_cb=CallbackData('bid_voting','bid_id','choice')
def bid_to_telegram(bid,person=None):
    kb = InlineKeyboardMarkup()
    votes = list(Vote.select().where(Vote.parent == bid))
    text = f'Заявка на бюджет в размере {bid.amount} от {bid.author.name} со средств {bid.parent_income.description} {bid.parent_income.amount}\n\t\tописание: {bid.description}\nГолоса:'
    persons = get_voting_persons()
    votes=bid.get_votes()
    for v in votes:
        if v.person in persons:
            text += f'\n{v.person.name}: {v.choice}'
            persons.remove(v.person)
    if not bid.closed:
        for pr in persons:
            text+=f"\n {pr.name}: Еще не проголосовал"
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
