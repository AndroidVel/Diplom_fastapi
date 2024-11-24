from backend.db import Base
from sqlalchemy import Column, Integer, String, Float
from models import *


class Product(Base):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    price = Column(Float, nullable=False)
    weight = Column(Float)
    image_url = Column(String, nullable=False)
