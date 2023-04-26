import sqlite3
import sqlalchemy
import os.path
from sqlalchemy import MetaData, Table, String, Integer, Column, Text, DateTime, Boolean, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

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
    city = Column(Integer)

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


def connect_to_DB():
    engine = create_engine('sqlite:///sqlite3.db')
    Base.metadata.create_all(engine)
    return engine









