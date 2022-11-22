from datetime import datetime

from peewee import BooleanField, DateTimeField, ForeignKeyField

from models import User
from models.person import get_role, Role, Person
from models.user import get_voting_persons
from models.transactions.Income import Income
from models.transactions.Transaction import TransactionBase



class Bid(TransactionBase): #vote for budget
    approved=BooleanField(default=False)
    time_approved=DateTimeField(default=None,null=True)
    parent_income=ForeignKeyField(Income,related_name='expense')
    def is_complete(self):
        votes=self.get_votes()
        users=get_voting_persons()
        return len(votes)>=len(users)
    def is_approved(self):
        aprrove_rating = self.calc_aprove_rating()
        return aprrove_rating>0.5 and self.is_complete()

    def calc_aprove_rating(self):
        votes = self.get_votes()
        aprrove_rating=0
        if any(votes):
            votes_yes = len(list(map(lambda x: x.choice == 1, votes)))
            aprrove_rating = votes_yes / len(votes)
        return aprrove_rating
    def get_votes(self):

        from models.transactions.votes.Vote import Vote
        return list(Vote.select().where(Vote.parent==self))
    def check_votes(self):
        res=self.is_approved()
        if not self.approved and res:
            self.approved=True
            self.time_approved=datetime.utcnow()
            self.save()
        return res