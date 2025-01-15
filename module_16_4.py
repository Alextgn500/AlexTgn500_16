from fastapi import FastAPI, status, Body, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

users_db = []

class User(BaseModel):
    id: int
    username: str
    age: int


@app.get("/")
async def get_all_users() -> List[User]:
    return users_db

@app.get(path="/user/{user_id}")
async def get_user(user_id: int) -> User:
    try:
        return users_db[user_id]
    except IndexError:
        raise HTTPException(status_code=404, detail="User not found")

@app.post("/user/{username}/{age}", response_model=User)
async def create_new_user(username: str, age: int) -> User:
    user_id = len(users_db) + 1
    new_user = User(id=user_id, username=username, age=age)
    users_db.append(new_user)

    print("Создан пользователь:", new_user)
    return new_user


@app.put("/user/{user_id}/{username}/{age}", response_model=User)
async def update_user(user_id: int, username: str, age: int) -> User:
    try:
        # Находим индекс пользователя с заданным id
        user_index = next(index for index, user in enumerate(users_db) if user.id == user_id)

        # Обновляем пользователя
        users_db[user_index].username = username
        users_db[user_index].age = age

        # Возвращаем обновленного пользователя
        return users_db[user_index]
    except StopIteration:
        raise HTTPException(status_code=404, detail="User not found")


@app.delete("/user/{user_id}", response_model=User)
async def delete_user(user_id: int) -> User:
    try:
        # Находим индекс пользователя с заданным id
        user_index = next(index for index, user in enumerate(users_db) if user.id == user_id)

        # Удаляем пользователя по найденному индексу
        deleted_user = users_db.pop(user_index)
        return deleted_user  # Возвращаем удаленного пользователя
    except StopIteration:
        raise HTTPException(status_code=404, detail="User not found")


@app.delete("/")
async def delete_user_all()-> str:
    users_db.clear()
    return "All users delete"








