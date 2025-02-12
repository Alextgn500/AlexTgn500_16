from fastapi import APIRouter, HTTPException, Depends, FastAPI
from sqlalchemy.orm import Session
from sqlalchemy import select

from slugify import slugify
from typing import List
from app.schemas.user_s import UserResponse, CreateUser, UpdateUser
from app.backend.db_depends import get_db


# Создаем экземпляр приложения
app = FastAPI(
    title="User API",  # название API
    description="API для управления пользователями",  # описание API
    version="1.0.0"  # версия API
)

router_user = APIRouter(prefix='/users', tags=['users'])

# Фейковые данные пользователей
fake_users = [
    {"id": 1, "username": "user1", "firstname": "john", "lastname": "Guy", "age": 25,
     "slug": "user1"},
    {"id": 2, "username": "user2", "firstname": "Jane", "lastname": "Smith", "age": 20,
     "slug": "user2"}
]

# Фейковые данные задач (добавляем в этот же файл)
fake_tasks = [
    {
        "id": 1,
        "title": "Complete project",
        "content": "Need to implement all CRUD operations",
        "priority": 1,
        "completed": False,
        "user_id": 1,
        "slug": "complete project"
    },
    {
        "id": 2,
        "title": "Write documentation",
        "content": "Create detailed API documentation",
        "priority": 2,
        "completed": False,
        "user_id": 1,
        "slug": "write documentation"
    },
    {
        "id": 3,
        "title": "Test API",
        "content": "Perform testing",
        "priority": 3,
        "completed": True,
        "user_id": 42,
        "slug": "test api"
    }
]


# Получение списка пользователей
@router_user.get("/users/", response_model=List[UserResponse])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    import importlib
    # Динамический импорт класса Users
    user_module = importlib.import_module('app.models.user_m')
    Users = user_module.Users  # Получаем доступ к классу Users

    result = db.execute(select(Users).offset(skip).limit(limit))
    users = result.scalars().all()
    return users


@router_user.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    import importlib
    # Динамический импорт класса Users
    user_module = importlib.import_module('app.models.user_m')
    Users = user_module.Users  # Получаем доступ к классу Users

    # Выполнение запроса к базе данных
    result = db.execute(select(Users).where(Users.id == user_id))  # Исправлено
    user = result.scalars().first()  # Исправлено
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


from sqlalchemy import and_


@router_user.post("/users/", response_model=UserResponse)
def create_user(user: CreateUser, db: Session = Depends(get_db)):
    import importlib
    # Динамический импорт класса Users
    user_module = importlib.import_module('app.models.user_m')
    Users = user_module.Users  # Получаем доступ к классу Users

    # Проверяем, существует ли пользователь с таким name и email
    existing_user = db.query(Users).filter(
        and_(Users.username == user.username, Users.firstname == user.firstname)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь с таким username и firsname уже существует")

    # Генерируем slug на основе имени
    user_slug = slugify(user.username)

    # Создаем нового пользователя, включая slug
    new_user = Users(**user.model_dump(), slug=user_slug)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Возвращаем ответ с обязательными полями
    return UserResponse(id=new_user.id, firstname=new_user.firstname, username=new_user.username,
                        lastname=new_user.lastname, age=new_user.age, slug=new_user.slug)

@router_user.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UpdateUser, db: Session = Depends(get_db)):
    import importlib
    # Динамический импорт класса Users
    user_module = importlib.import_module('app.models.user_m')
    Users = user_module.Users  # Получаем доступ к классу Users

    existing_user = db.get(Users, user_id)
    if existing_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Обновляем поля пользователя
    for key, value in user.dict(exclude_unset=True).items():
        setattr(existing_user, key, value)

    # Обновляем slug на основе username
    existing_user.slug = slugify(existing_user.username)

    db.commit()  # Не забудьте вызвать commit как метод
    db.refresh(existing_user)  # Не забудьте вызвать refresh как метод

    return UserResponse(
        id=existing_user.id,
        username=existing_user.username,
        firstname=existing_user.firstname,
        lastname=existing_user.lastname,
        age=existing_user.age,
        slug=existing_user.slug
    )

@router_user.delete("/users/{user_id}/tasks", response_model=dict)
def delete(user_id: int, db: Session = Depends(get_db)):
    import importlib
    # Динамический импорт класса Users
    user_module = importlib.import_module('app.models.user_m')
    Users = user_module.Users  # Получаем доступ к классу Users

    # Находим существующего пользователя
    existing_user = db.get(Users, user_id)
    if existing_user is None:
        raise HTTPException(status_code=404, detail="User not found")

        # Динамический импорт модуля task_m
    task_module = importlib.import_module('app.models.task_m')  # Импортируем модуль task_m
    Tasks = task_module.Tasks  # Получаем доступ к классу Tasks

    # Удаляем связанные задачи
    db.query(Tasks).filter(Tasks.user_id == user_id).delete(synchronize_session=False)

    # Удаляем пользователя
    db.delete(existing_user)  # Удаляем пользователя, если он существует

    db.commit()  # Коммитим изменения

    return {"detail": "User and associated tasks deleted successfully"}
