"""Peewee migrations -- 003_wallet.py.

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

    migrator.add_index('income', 'id', unique=True)

    migrator.add_index('bid', 'id', unique=True)

    migrator.add_index('expanse', 'id', unique=True)

    migrator.add_index('transaction', 'id', unique=True)

    migrator.add_index('transactionbase', 'id', unique=True)

    migrator.add_fields(
        'users',

        wallet=pw.ForeignKeyField(backref='user_set', column_name='wallet_id', field='id', model=migrator.orm['wallet'], null=True))

    @migrator.create_model
    class WalletPermission(pw.Model):
        id = pw.AutoField()
        wallet = pw.ForeignKeyField(backref='walletpermission_set', column_name='wallet_id', field='id', model=migrator.orm['wallet'])
        person = pw.ForeignKeyField(backref='wallets_permission', column_name='person_id', field='id', model=migrator.orm['person'])

        class Meta:
            table_name = "walletpermission"



def rollback(migrator: Migrator, database, fake=False, **kwargs):
    """Write your rollback migrations here."""

    migrator.change_fields('vote', created_at=pw.DateTimeField(constraints=[SQL("DEFAULT datetime.datetime(2022, 11, 26, 0, 28, 53, 490117)")], default=datetime.datetime(2022, 11, 26, 0, 28, 53, 490117)))

    migrator.remove_fields('users', 'wallet')

    migrator.drop_index('transactionbase', 'id')

    migrator.drop_index('transaction', 'id')

    migrator.drop_index('expanse', 'id')

    migrator.drop_index('bid', 'id')

    migrator.drop_index('income', 'id')

    migrator.remove_model('walletpermission')
