from fastapi import FastAPI, Path
from pydantic import BaseModel
from typing import Annotated

app = FastAPI()


# Модель валидации пользователя
class UserModel(BaseModel):
    username: Annotated[str, Path(min_length=4, max_length=20)]
    age: Annotated[int, Path(ge=18, le=120)]


# Начальный словарь пользователей
users = {'1': 'Имя: Example, возраст: 18'}

@app.get('/users')
def get_users():
    return users

# Первый POST-запрос (второй пользователь)
@app.post('/user/{username}/{age}')
def create_second_user(
        username: Annotated[str, Path(min_length=4, max_length=20, description="Имя пользователя", examples="UrbanUser")],
        age: Annotated[int, Path(ge=18, le=120, description="Возраст пользователя", examples=24)]
):
    # Валидация через Pydantic
    UserModel(username=username, age=age)

    # Создаем ID для второго пользователя
    user_id = '2'

    # Добавляем пользователя
    users[user_id] = f'Имя: {username}, возраст: {age}'
    return f'User {user_id} is registered'


# Второй POST-запрос (третий пользователь)
@app.post('/user2/{username}/{age}')
def create_third_user(
        username: Annotated[str, Path(min_length=4, max_length=20,
                    description="Имя нового пользователя", examples="NewUser")],
        age: Annotated[int, Path(ge=18, le=120, description="Возраст нового пользователя",
                    examples=22)]
):
    # Валидация через Pydantic
    UserModel(username=username, age=age)

    # Создаем ID для третьего пользователя
    user_id = '3'

    # Добавляем пользователя
    users[user_id] = f'Имя: {username}, возраст: {age}'
    return f'User {user_id} is registered'

@app.put('/user/{user_id}/{username}/{age}')
def update_user(
        user_id: Annotated[str, Path(title="Update ID of the user")],
        username: Annotated[str, Path(min_length=4, max_length=20, description="Имя добавленного пользоватея",
                                      examples="UrbanProfi")],
        age: Annotated[int, Path(ge=18, le=120, description="Возраст добавленного пользователя",
                                 examples= 28)]
):
    # Валидация через Pydantic
    UserModel(username=username, age=age)

    # Проверка существования пользователя
    if user_id not in users:
        return f'User {user_id} not found'

    # Обновление пользователя
    users[user_id] = f'Имя: {username}, возраст: {age}'
    return f'User {user_id} has been updated'


@app.delete('/user/{user_id}')
def delete_user(user_id: Annotated[str, Path()]):
    # Проверка существования пользователя
    if user_id not in users:
        return f'User {user_id} not found'

    # Удаление пользователя
    del users[user_id]
    return f'User {user_id} has been deleted'

@app.get('/users')  # Финальный просмотр после удаления
def get_users_after_delete():
    return users
