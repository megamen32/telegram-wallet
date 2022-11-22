from peewee import BooleanField, DateTimeField, ForeignKeyField

from models import User
from models.transactions.Transaction import TransactionBase



class Bid(TransactionBase): #vote for budget
    approved=BooleanField(default=False)
    time_approved=DateTimeField()
    def is_complete(self):
        votes=self.get_votes()
        users=User.select(User.person.role.is_voting())
        return len(votes)==len(users)
    def is_approved(self):
        votes = self.get_votes()
        votes_yes=len(list(map(lambda x:x.choice==1, votes)))
        aprrove_rating=votes_yes/len(votes)
        return aprrove_rating>0.5 and self.is_complete()

