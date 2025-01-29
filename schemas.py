from typing import Optional
from pydantic import BaseModel

class UserBase(BaseModel):
    username: str
    firstname: str
    lastname: str
    age: int


class CreateUser(UserBase):
    pass

class UpdateUser(BaseModel):
    username: Optional[str] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    age: Optional[int] = None


    class Config:
        from_attributes = True


class UserResponse(UserBase):
    id: int
    slug: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "john_doe",
                "firstname": "John",
                "lastname": "Doe",
                "age": 30,
                "slug": "john-doe"
            }
        }


class CreateTask(BaseModel):
    title: str
    content: str
    priority: int

    class Config:
        from_attributes = True


class UpdateTask(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    priority: Optional[int] = None

    class Config:
        from_attributes = True
