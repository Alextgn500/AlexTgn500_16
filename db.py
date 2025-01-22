# app/backend/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = 'sqlite:///database.db'

engine = create_engine('sqlite:///taskmanager.db')
Session = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass
