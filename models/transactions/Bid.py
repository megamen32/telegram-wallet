import asyncio
import operator
import traceback
from datetime import datetime

from peewee import BooleanField, DateTimeField, ForeignKeyField, fn

from models import User
from models.person import get_role, Role, Person
from models.user import get_voting_persons
from models.transactions.Income import Income
from models.transactions.Transaction import TransactionBase


class Bid(TransactionBase):  # vote for budget
    closed = BooleanField(default=False)  # решение уже вынесено
    approved = BooleanField(default=False)  # какое решение было вынесено по заявки
    time_approved = DateTimeField(default=None, null=True)
    parent_income = ForeignKeyField(Income, backref='expenses')

    def is_complete(self):
        votes = self.get_votes()
        users = get_voting_persons(self.wallet)
        return len(votes) >= len(users)

    def is_approved(self):
        aprrove_rating = self.calc_aprove_rating()
        return aprrove_rating > 0.5 and self.is_complete()

    def get_expenses(self):
        from models.transactions.Expense import Expanse
        expanses = list(Expanse.select(Expanse).where(Expanse.parent_bid == self))
        return expanses

    def get_expenses_amount(self):
        amount = sum(map(operator.attrgetter('amount'), self.get_expenses()))
        return amount

    @property
    def was_used(self):
        return self.amount < self.get_expenses_amount()

    def status(self):
        if self.was_used:
            return 'потрачено ❌'
        if self.closed:
            if self.approved:
                text = 'принята ✅'
            else:
                text = 'отклонена ⛔'
        else:
            text = 'ждёт согласования 🟨'
        return text

    def calc_aprove_rating(self):
        votes = self.get_votes()
        aprrove_rating = 0
        if any(votes):
            votes_yes = len(list(filter(lambda x: x.choice == 1, votes)))
            aprrove_rating = votes_yes / len(votes)
        return aprrove_rating

    def get_votes(self):

        from models.transactions.votes.Vote import Vote
        return list(Vote.select().where(Vote.parent == self))

    def check_votes(self):
        res = self.is_approved()
        if not self.closed and self.is_complete():
            self.closed = True
            self.time_approved = datetime.utcnow()
            self.approved = res
            self.save()

            try:
                user = User.get(User.person == self.author)
                from loader import bot, dp
                from aiogram import types
                from bot.handlers.wallet.bid import bid_cb

                kb = types.InlineKeyboardMarkup()
                if self.approved:
                    asyncio.create_task(dp.storage.set_data(chat=user.id, data={'amount': self.amount,
                                                                                'description': self.description}))
                    kb.add(types.InlineKeyboardButton(f"Создать трату на эту сумму",
                                                      callback_data=bid_cb.new(bid=self.id)))
                asyncio.create_task(bot.send_message(user.id,
                                                     f'Заявка {self.description} {self.amount} Закрыта со статусом:{self.status()}',
                                                     reply_markup=kb))
            except:
                traceback.print_exc()
        return res
