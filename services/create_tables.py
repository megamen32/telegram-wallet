from models.person import Person,Role
from models.user import User
from loader import database
def create_tables():
    with database:
        database.create_tables([Role,Person,User,Transaction,Expanse,Income,Vote,Bid])
if __name__=='__main__':
    create_tables()