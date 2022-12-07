from models.base import BaseModel
from peewee import DoesNotExist,OperationalError, CharField, ForeignKeyField

roles=['guest','user','admin']


class Role(BaseModel):
    role=CharField(index=True,unique=True)
    def is_admin(self):
        return self.role=='admin'

    def __repr__(self) -> str:
        return f'<role {self.role}>'
    def __str__(self):
        return self.role

def create_default_roles():
    return [Role.create(role=role) for role in roles]
def get_role(role:str)->Role:
    try:
        return Role.get(Role.role==role)
    except (OperationalError,DoesNotExist):
        create_default_roles()
        return get_role(role)

class Person(BaseModel):
    name=CharField(index=True,unique=True)
    role=ForeignKeyField(Role,related_name='roles')
    def __repr__(self) -> str:
        return f'<Person {self.name}>'

    def __str__(self):
        return self.name


def get_default_user()->Person:
    person=Person()
    person.name='guest'
    person.role=get_role('guest')
    return person
