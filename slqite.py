
import random
from sqlalchemy import ForeignKey
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User1():
    def __init__(self, _id, _gender, _city):
        self.id = _id
        self.gender = _gender
        self.city = _city

    def set_id(self, _id):
        self.id = _id

    def get_id(self):
        return self.id

    def set_gender(self, _gender):
        self.gender = _gender

    def get_gender(self):
        return self.gender

    def set_city(self, _city):
        self.city = _city

    def get_city(self):
        return self.city

class User(Base):
    __tablename__ = 'User'
    id = Column(Integer, primary_key= True)
    gender = Column(String)
    city = Column(String)

    def __init__(self):
        self.id = None
        self.gender = None
        self.city = None

    def set_id(self, _id):
        self.id = _id

    def get_id(self):
        return self.id

    def set_gender(self, _gender):
        self.gender = _gender

    def get_gender(self):
        return self.gender

    def set_city(self, _city):
        self.city = _city

    def get_city(self):
        return self.city

class Clothes(Base):
    __tablename__ = 'Сlothes'
    id = Column(Integer, primary_key=True)
    type = Column(String)
    file_name = Column(String)
    user_id = Column(Integer, ForeignKey('User.id'))
    user = relationship('User', backref='clothes')

    def __init__(self):
        self.type = None
        self.file_name = None

    def set_type(self, _type):
        self.type = _type

    def get_type(self):
        return self.type

    def set_file_name(self, _file_name):
        self.file_name = _file_name

    def get_file_name(self):
        return self.file_name

    def set_user_id(self, _user_id):
        self.user_id = _user_id

    def get_user_id(self):
        return self.user_id


def connect_to_DB():
    engine = create_engine('sqlite:///sqlite3.db')
    Base.metadata.create_all(engine)
    return engine



#'футболка', 'брюки', 'свитер', 'платье', 'куртка', 'туфли', 'рубашка', 'кроссовки', 'сумка','ботинки'
def get_clothes(session, id, temp):
    print(type(id))
    clothes_type2 = session.query(Clothes).filter(Clothes.type == 'брюки', Clothes.user_id == id).all()
    if temp < 10:
        clothes_type1 = session.query(Clothes).filter(
            Clothes.type.in_(['куртка']), Clothes.user_id == id).all()
    elif temp > 20:
        clothes_type1 = session.query(Clothes).filter(
            Clothes.type.in_(['футболка','рубашка','платье']), Clothes.user_id == id).all()
    else:
        clothes_type1 = session.query(Clothes).filter(
            Clothes.type.in_(['свитер','сумка']), Clothes.user_id == id).all()
    if clothes_type1 and clothes_type2:
        random_clothes1 = random.choice(clothes_type1)
        random_clothes2 = random.choice(clothes_type2)
        return random_clothes1.get_file_name(), random_clothes2.get_file_name()
    elif clothes_type1:
        random_clothes1 = random.choice(clothes_type1)
        return random_clothes1.get_file_name(), None
    elif clothes_type2:
        random_clothes2 = random.choice(clothes_type2)
        return None, random_clothes2.get_file_name()
    return None, None






