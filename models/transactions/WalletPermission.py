from peewee import ForeignKeyField

from models.base import BaseModel
from models.person import Person
from models.transactions.Transaction import Wallet


class WalletPermission(BaseModel):
    wallet=ForeignKeyField(Wallet,on_delete='CASCADE')
    person=ForeignKeyField(Person,backref='wallets_permission',on_delete='CASCADE')
