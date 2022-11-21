from peewee import *
db=SqliteDatabase('wallet.db')

class Person(Model):
    username = CharField(index=True)
    class Meta:
        database =  db  # модель будет использовать базу данных 'views.db'
class TelegramClient(Model):
    person=ForeignKeyField(Person,related_name='author')
    telegram_id=CharField(primary_key=True)
    telegram_name=CharField()
class Transaction(Model):
    time_created = DateTimeField()
    amount = FloatField()
    description=CharField()
    id=AutoField(primary_key=True,unique=True)
    author=ForeignKeyField(Person)

    class Meta:
        database = db  # модель будет использовать базу данных 'people.db'
class Income(Transaction):
    pass
class VoteBudjet(Transaction):
    aprroved=BooleanField()
    time_approved=DateTimeField()
class Vote(Model):
    person=ForeignKeyField(Person,related_name='voters')
    choice=IntegerField()
    parent=ForeignKeyField(VoteBudjet,related_name='parent')

    class Meta:
        database = db  # модель будет использовать базу данных 'people.db'

class Spending(Transaction):
    parent_income=ForeignKeyField(Income,related_name='spendings')
    parent_vote=ForeignKeyField(VoteBudjet,related_name='vote')



