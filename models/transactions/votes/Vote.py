from peewee import Model, ForeignKeyField, IntegerField

from models.base import  BaseModel
from models.person import Person
from models.transactions.Bid import Bid


class Vote(BaseModel):
    person=ForeignKeyField(Person,related_name='voters')
    choice=IntegerField()
    parent=ForeignKeyField(Bid, related_name='parent')

def get_votes(bid):
    return Vote.select(Vote.parent==bid)