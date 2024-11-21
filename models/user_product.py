from sqlalchemy import Column, ForeignKey, Table, Integer
from backend.db import Base
from models import *


user_product = Table('user_product', Base.metadata,
                     Column('user_id', Integer, ForeignKey('user.id'), primary_key=True),
                     Column('product_id', Integer, ForeignKey('product.id'), primary_key=True)
                     )
