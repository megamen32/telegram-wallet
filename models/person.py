from models.base import BaseModel
from peewee import DoesNotExist,OperationalError,BigIntegerField, CharField, BooleanField, DateTimeField, ForeignKeyField

roles=['guest','user','voting','admin']


class Role(BaseModel):
    role=CharField()
    def is_admin(self):
        return self.role=='admin'
    def is_voting(self):
        return self.role=='voting' or self.role=='admin'
    def is_user(self):
        return self.role=='voting' or self.role=='user' or self.role=='user'

def create_default_roles():
    return [Role.create(role=role) for role in roles]
def get_role(role:str)->Role:
    try:
        return Role.get(Role.role==role)
    except (OperationalError,DoesNotExist):
        create_default_roles()
        return get_role(role)

class Person(BaseModel):
    name=CharField(index=True)
    role=ForeignKeyField(Role,related_name='roles')
    def __repr__(self) -> str:
        return f'<Person {self.name}>'
def get_default_user()->Person:
    person=Person()
    person.name='guest'
    person.role=get_role('guest')
    return person
