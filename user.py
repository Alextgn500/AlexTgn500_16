from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.backend.db import Base
from pydantic import BaseModel
from typing import Optional

# Pydantic модели
class UserBase(BaseModel):
    username: str
    firstname: str
    lastname: str
    age: int


class CreateUser(UserBase):
    user_id: int  # Изменено с id на user_id для соответствия с router

class UpdateUser(UserBase):
    username: Optional[str] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    age: Optional[int] = None
    user_id: Optional[int] = None


class UserResponse(UserBase):
    id: int
    slug: str


# SQLAlchemy модель
class User(Base):
    __tablename__ = 'users'  # Исправлено: добавлены двойные подчеркивания
    __table_args__ = {"extend_existing": True}  # Исправлено: добавлены двойные подчеркивания

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    slug = Column(String, unique=True, index=True)

    tasks = relationship('Task', back_populates='user')
