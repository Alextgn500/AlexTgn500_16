from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from pathlib import Path

app = FastAPI()
BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# Модель пользователя
class User(BaseModel):
    id: int = None
    username: str
    age: int


# Модель для обновления пользователя
class UserUpdate(BaseModel):
    username: str
    age: int


# База данных в памяти
users_db = []
current_id = 1


# Маршрут для главной страницы со списком пользователей
@app.get("/", response_class=HTMLResponse)
async def get_users(request: Request):
    return templates.TemplateResponse(
        "users.html",
        {"request": request, "users": users_db}
    )


# Маршрут для получения конкретного пользователя
@app.get("/user/{user_id}", response_class=HTMLResponse)
async def get_user(request: Request, user_id: int):
    user = next((user for user in users_db if user.id == user_id), None)
    return templates.TemplateResponse(
        "users.html",
        {"request": request, "user": User}
    )


# Маршрут для создания нового пользователя
@app.post("/user", response_class=HTMLResponse)
async def create_user(request: Request, username: str = Form(...), age: int = Form(...)):
    global current_id
    new_user = User(id=current_id, username=username, age=age)
    users_db.append(new_user)
    current_id += 1
    return templates.TemplateResponse(
        "users.html",
        {"request": request, "users": users_db}
    )


# Маршрут для обновления пользователя
@app.put("/user/{user_id}")
async def update_user(user_id: int, user_update: UserUpdate):
    user = next((user for user in users_db if user.id == user_id), None)
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Обновляем данные пользователя
    user.username = user_update.username
    user.age = user_update.age

    return {"message": "Данные пользователя обновлены", "user": user}


# Маршрут для удаления пользователя
@app.delete("/user/{user_id}")
async def delete_user(user_id: int):
    user = next((user for user in users_db if user.id == user_id), None)
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    users_db.remove(user)
    return {"message": "Пользователь успешно удален"}
