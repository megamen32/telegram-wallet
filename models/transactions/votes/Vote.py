import datetime

from peewee import Model, ForeignKeyField, IntegerField, DateTimeField

from models.base import  BaseModel
from models.person import Person
from models.transactions.Bid import Bid


class Vote(BaseModel):
    person=ForeignKeyField(Person,related_name='voters',backref='votes')
    choice=IntegerField()
    parent=ForeignKeyField(Bid, related_name='parent',backref='votes',on_delete='CASCADE')
    created_at=DateTimeField(default=lambda :datetime.datetime.utcnow())

