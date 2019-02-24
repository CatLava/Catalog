#!/usr/bin/python2.7

import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    email = Column(String(80), nullable=False)
    picture = Column(String(80), nullable=False)


class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    item_name = Column(String(80), nullable=False)
    description = Column(String(250))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            "item_name": self.item_name,
            "id": self.id,
            "description": self.description
        }


class Item_adds(Base):
    __tablename__ = 'item_adds'

    id = Column(Integer, primary_key=True)
    item_add_name = Column(String(80), nullable=False)
    description = Column(String(250))
    item_id = Column(Integer, ForeignKey('item.id'))
    item = relationship(Item)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            "name": self.item_add_name,
            "description": self.description,
            "id": self.id
        }


engine = create_engine('sqlite:///catalog.db')

Base.metadata.create_all(engine)
