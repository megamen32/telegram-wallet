import logging
from datetime import datetime

from peewee import PrimaryKeyField,DateTimeField, FloatField, CharField, AutoField, ForeignKeyField

from models.base import BaseModel
from models.person import Person



class Wallet(BaseModel):
    id=PrimaryKeyField(primary_key=True)
    start_balance=FloatField(default=0)

def get_default_wallet(person):
    try:

        from models.transactions.WalletPermission import WalletPermission
        res=list(Wallet.select().join(WalletPermission).join(Person).where(Person.name==person.name))[0]
        return res
    except:
        logging.info(f'Creating wallet for {person}')
class TransactionBase(BaseModel):
    wallet = ForeignKeyField(Wallet, related_name='wallets',on_delete='CASCADE')
    created_at = DateTimeField(default=lambda: datetime.utcnow())
    amount = FloatField(default=0)
    description = CharField(default='')
    id = PrimaryKeyField(primary_key=True, unique=True)
    author = ForeignKeyField(Person)
class Transaction(TransactionBase):
    pass

