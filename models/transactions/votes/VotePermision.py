import datetime

from peewee import Model, ForeignKeyField, IntegerField, DateTimeField

from models.base import  BaseModel
from models.person import Person
from models.transactions.Transaction import Wallet


def VotePermision(BaseModel):
    person = ForeignKeyField(Person,  backref='vote_permisions')
    wallet = ForeignKeyField(Wallet)
    created_at = DateTimeField(default=lambda: datetime.datetime.utcnow())
