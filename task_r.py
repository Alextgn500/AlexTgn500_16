from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from typing import List
from slugify import slugify

from app.schemas.user_s import TaskResponse, CreateTask
from app.backend.db_depends import get_db

router_task = APIRouter(prefix='/tasks', tags=['tasks'])

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

@router_task.get("/tasks/", response_model=List[TaskResponse])
def all_tasks(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    import importlib
    # Динамический импорт класса Tasks
    task_module = importlib.import_module('app.models.task_m')  # Импортируем модуль task_m
    Tasks = task_module.Tasks  # Получаем доступ к классу Tasks

    # Получаем все задачи из базы данных с использованием skip и limit
    result = db.execute(select(Tasks).offset(skip).limit(limit))
    tasks = result.scalars().all()  # Получаем все задачи

    return tasks


@router_task.get("tasks/{task_id}", response_model=TaskResponse)
def task_by_id(task_id: int, db: Session = Depends(get_db)):
    import importlib
    task_module = importlib.import_module('app.models.task_m')  # Импортируем модуль task_m
    Tasks = task_module.Tasks  # Получаем доступ к классу Tasks

    result = db.execute(select(Tasks).where(Tasks.id == task_id))
    task = result.scalars().first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


@router_task.post("/tasks/", response_model=TaskResponse)
def create_task(task: CreateTask, db: Session = Depends(get_db)):
    import importlib
    task_module = importlib.import_module('app.models.task_m')  # Импортируем модуль task_m
    Tasks = task_module.Tasks  # Получаем доступ к классу Tasks

    # Проверяем, существует ли пользователь с таким name и email
    existing_task = db.query(Tasks).filter(Tasks.title == task.title).first()
    if existing_task:
        raise HTTPException(status_code=400, detail="Такая существует")

    # Генерируем slug на основе title
    task_slug = slugify(task.title)

    db_task = Tasks(
        title=task.title,
        content=task.content,
        priority=task.priority,
        completed=task.completed,
        user_id=task.user_id,
        slug=task.slug
    )
    # Добавляем задачу в базу данных
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return TaskResponse(
        id=db_task.id,
        title=db_task.title,
        content=db_task.content,
        priority=db_task.priority,
        completed=db_task.completed,
        user_id=db_task.user_id,
        slug=db_task.slug
    )

@router_task.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task: CreateTask, db: Session = Depends(get_db)):
    import importlib
    task_module = importlib.import_module('app.models.task_m')  # Импортируем модуль task_m
    Tasks = task_module.Tasks  # Получаем доступ к классу Tasks
    result = db.execute(select(Tasks).where(Tasks.id == task_id))
    db_task = result.scalar_one_or_none()

    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    for key, value in task.dict(exclude_unset=True).items():
        setattr(db_task, key, value)

    db.commit()
    db.refresh(db_task)
    return db_task

@router_task.delete("/tasks/{task_id}", response_model=dict)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    import importlib
    task_module = importlib.import_module('app.models.task_m')  # Импортируем модуль task_m
    Tasks = task_module.Tasks  # Получаем доступ к классу Tasks
    result = db.execute(select(Tasks).where(Tasks.id == task_id))
    db_task = result.scalar_one_or_none()

    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(db_task)
    db.commit()
    return {"detail": "Task deleted successfully"}
