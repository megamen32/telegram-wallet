from models.person import Person,Role
from models.transactions.Bid import Bid
from models.transactions.Expense import Expanse
from models.transactions.Income import Income
from models.transactions.Transaction import Transaction, Wallet
from models.transactions.votes.Vote import Vote
from models.transactions.votes.VotePermission import VotePermission
from models.user import User
from loader import database
def create_tables():
    with database:
        database.create_tables([Role, Person, User, Transaction, Expanse, Income, Vote, Bid, Wallet, VotePermission])
if __name__=='__main__':
    create_tables()