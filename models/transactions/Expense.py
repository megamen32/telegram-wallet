from peewee import ForeignKeyField

from models.transactions.Income import Income
from models.transactions.Transaction import Transaction
from models.transactions.Bid import Bid


class Expanse(Transaction):
    parent_bid=ForeignKeyField(Bid, related_name='bids',backref='expenses')
