from fastapi import FastAPI, Path, HTTPException
from pydantic import BaseModel, Field
from typing import Dict

app = FastAPI()

# Модель валидации пользователя
class UserModel(BaseModel):
    username: str = Field(..., min_length=4, max_length=20)
    age: int = Field(..., ge=18, le=120)

# Начальный словарь пользователей
users_db: Dict[str, str] = {'1': 'Имя: Example, возраст: 18'}

@app.get('/users')  
async def get_users():
    return users_db

# POST-запрос (новый пользователь)
@app.post('/user/{username}/{age}')  
async def create_new_user(
        username: str = Path(..., min_length=4, max_length=20, description="Имя пользователя"),
        age: int = Path(..., ge=18, le=120, description="Возраст пользователя")
):
    # Валидация через Pydantic
    user_model = UserModel(username=username, age=age)

    # Создаем ID для нового пользователя
    user_id = str(len(users_db) + 1)
    users_db[user_id] = f'Имя: {username}, возраст: {age}'
    return f'User {user_id} is registered'

@app.put('/user/{user_id}/{username}/{age}')  
async def update_user(
        user_id: str = Path(..., title="Update ID of the user"),
        username: str = Path(..., min_length=4, max_length=20, description="Имя добавленного пользователя"),
        age: int = Path(..., ge=18, le=120, description="Возраст добавленного пользователя")
):
    # Валидация через Pydantic
    user_model = UserModel(username=username, age=age)

    # Проверка существования пользователя
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail=f'User {user_id} not found')

    # Обновление пользователя
    users_db[user_id] = f'Имя: {username}, возраст: {age}'
    return f'User {user_id} has been updated'

@app.delete('/user/{user_id}') 
async def delete_user(user_id: str = Path(...)):
    # Проверка существования пользователя
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail=f'User {user_id} not found')

    # Удаление пользователя
    del users_db[user_id]
    return f'User {user_id} has been deleted'

@app.get('/users')  
async def get_users_after_delete():
    return users_db
