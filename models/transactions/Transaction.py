import logging
from datetime import datetime

from peewee import PrimaryKeyField,DateTimeField, FloatField, CharField, AutoField, ForeignKeyField

from models.base import BaseModel
from models.person import Person

class Wallet(BaseModel):
    id=PrimaryKeyField(primary_key=True)
    start_balance=FloatField(default=0)

def get_default_wallet():
    try:
        res=Wallet.get()
        return res
    except:
        logging.info('Creating wallet')
        res=Wallet.create()
        return res
class TransactionBase(BaseModel):
    wallet = ForeignKeyField(Wallet, related_name='wallets')
    created_at = DateTimeField(default=lambda: datetime.utcnow())
    amount = FloatField(default=0)
    description = CharField(default='')
    id = PrimaryKeyField(primary_key=True, unique=True)
    author = ForeignKeyField(Person)
class Transaction(TransactionBase):
    pass
