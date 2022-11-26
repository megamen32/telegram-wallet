"""Peewee migrations -- 001_wallet.py.

Some examples (model - class or model name)::

    > Model = migrator.orm['model_name']            # Return model in current state by name

    > migrator.sql(sql)                             # Run custom SQL
    > migrator.python(func, *args, **kwargs)        # Run python code
    > migrator.create_model(Model)                  # Create a model (could be used as decorator)
    > migrator.remove_model(model, cascade=True)    # Remove a model
    > migrator.add_fields(model, **fields)          # Add fields to a model
    > migrator.change_fields(model, **fields)       # Change fields
    > migrator.remove_fields(model, *field_names, cascade=True)
    > migrator.rename_field(model, old_field_name, new_field_name)
    > migrator.rename_table(model, new_table_name)
    > migrator.add_index(model, *col_names, unique=False)
    > migrator.drop_index(model, *col_names)
    > migrator.add_not_null(model, *field_names)
    > migrator.drop_not_null(model, *field_names)
    > migrator.add_default(model, field_name, default)

"""

import datetime as dt
import peewee as pw
from peewee_migrate import Migrator
from decimal import ROUND_HALF_EVEN

try:
    import playhouse.postgres_ext as pw_pext
except ImportError:
    pass

SQL = pw.SQL


def migrate(migrator: Migrator, database, fake=False, **kwargs):
    """Write your migrations here."""

    @migrator.create_model
    class BaseModel(pw.Model):
        id = pw.AutoField()

        class Meta:
            table_name = "basemodel"

    @migrator.create_model
    class Role(pw.Model):
        id = pw.AutoField()
        role = pw.CharField(max_length=255, unique=True)

        class Meta:
            table_name = "role"

    @migrator.create_model
    class Person(pw.Model):
        id = pw.AutoField()
        name = pw.CharField(max_length=255, unique=True)
        role = pw.ForeignKeyField(backref='roles', column_name='role_id', field='id', model=migrator.orm['role'])

        class Meta:
            table_name = "person"

    @migrator.create_model
    class Wallet(pw.Model):
        start_balance = pw.FloatField(constraints=[SQL("DEFAULT 0")], default=0)

        class Meta:
            table_name = "wallet"
    @migrator.create_model
    class Income(pw.Model):
        wallet = pw.ForeignKeyField(backref='income_set', column_name='wallet_id', field='id', model=migrator.orm['wallet'])
        created_at = pw.DateTimeField()
        amount = pw.FloatField(constraints=[SQL("DEFAULT 0")], default=0)
        description = pw.CharField(constraints=[SQL("DEFAULT ''")], default='', max_length=255)
        author = pw.ForeignKeyField(backref='income_set', column_name='author_id', field='id', model=migrator.orm['person'])

        class Meta:
            table_name = "income"



    @migrator.create_model
    class Bid(pw.Model):
        wallet = pw.ForeignKeyField(backref='bid_set', column_name='wallet_id', field='id', model=migrator.orm['wallet'])
        created_at = pw.DateTimeField()
        amount = pw.FloatField(constraints=[SQL("DEFAULT 0")], default=0)
        description = pw.CharField(constraints=[SQL("DEFAULT ''")], default='', max_length=255)
        author = pw.ForeignKeyField(backref='bid_set', column_name='author_id', field='id', model=migrator.orm['person'])
        closed = pw.BooleanField(constraints=[SQL("DEFAULT False")], default=False)
        was_used = pw.BooleanField(constraints=[SQL("DEFAULT False")], default=False)
        approved = pw.BooleanField(constraints=[SQL("DEFAULT False")], default=False)
        time_approved = pw.DateTimeField(null=True)
        parent_income = pw.ForeignKeyField(backref='expense', column_name='parent_income_id', field='id', model=migrator.orm['income'])

        class Meta:
            table_name = "bid"

    @migrator.create_model
    class Expanse(pw.Model):
        wallet = pw.ForeignKeyField(backref='expanse_set', column_name='wallet_id', field='id', model=migrator.orm['wallet'])
        created_at = pw.DateTimeField()
        amount = pw.FloatField(constraints=[SQL("DEFAULT 0")], default=0)
        description = pw.CharField(constraints=[SQL("DEFAULT ''")], default='', max_length=255)
        author = pw.ForeignKeyField(backref='expanse_set', column_name='author_id', field='id', model=migrator.orm['person'])
        parent_bid = pw.ForeignKeyField(backref='bids', column_name='parent_bid_id', field='id', model=migrator.orm['bid'])

        class Meta:
            table_name = "expanse"

    @migrator.create_model
    class Transaction(pw.Model):
        wallet = pw.ForeignKeyField(backref='transaction_set', column_name='wallet_id', field='id', model=migrator.orm['wallet'])
        created_at = pw.DateTimeField()
        amount = pw.FloatField(constraints=[SQL("DEFAULT 0")], default=0)
        description = pw.CharField(constraints=[SQL("DEFAULT ''")], default='', max_length=255)
        author = pw.ForeignKeyField(backref='transaction_set', column_name='author_id', field='id', model=migrator.orm['person'])

        class Meta:
            table_name = "transaction"



    @migrator.create_model
    class TransactionBase(pw.Model):
        wallet = pw.ForeignKeyField(backref='wallets', column_name='wallet_id', field='id', model=migrator.orm['wallet'])
        created_at = pw.DateTimeField()
        amount = pw.FloatField(constraints=[SQL("DEFAULT 0")], default=0)
        description = pw.CharField(constraints=[SQL("DEFAULT ''")], default='', max_length=255)
        author = pw.ForeignKeyField(backref='transactionbase_set', column_name='author_id', field='id', model=migrator.orm['person'])

        class Meta:
            table_name = "transactionbase"

    @migrator.create_model
    class User(pw.Model):
        id = pw.BigIntegerField(primary_key=True)
        name = pw.CharField(max_length=255)
        person = pw.ForeignKeyField(backref='user_set', column_name='person_id', field='id', model=migrator.orm['person'], null=True)
        username = pw.CharField(max_length=255, null=True)
        language = pw.CharField(constraints=[SQL("DEFAULT 'en'")], default='en', max_length=255)
        is_admin = pw.BooleanField(constraints=[SQL("DEFAULT False")], default=False)
        created_at = pw.DateTimeField()

        class Meta:
            table_name = "users"

    @migrator.create_model
    class Vote(pw.Model):
        id = pw.AutoField()
        person = pw.ForeignKeyField(backref='voters', column_name='person_id', field='id', model=migrator.orm['person'])
        choice = pw.IntegerField()
        parent = pw.ForeignKeyField(backref='parent', column_name='parent_id', field='id', model=migrator.orm['bid'])

        class Meta:
            table_name = "vote"



def rollback(migrator: Migrator, database, fake=False, **kwargs):
    """Write your rollback migrations here."""

    migrator.remove_model('vote')

    migrator.remove_model('users')

    migrator.remove_model('transactionbase')

    migrator.remove_model('transaction')

    migrator.remove_model('wallet')

    migrator.remove_model('income')

    migrator.remove_model('expanse')

    migrator.remove_model('bid')

    migrator.remove_model('person')

    migrator.remove_model('role')

    migrator.remove_model('basemodel')
