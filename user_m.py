from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from sqlalchemy import select, insert, update, delete
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Annotated
from slugify import slugify
from app.backend.db_depends import get_db
from app.models import User
from app.models.user import UserResponse
from app.schemas import CreateUser, UpdateUser, UserResponse
import uvicorn

# Создаем экземпляр приложения
app = FastAPI(
    title="User API",  # название API
    description="API для управления пользователями",  # описание API
    version="1.0.0"  # версия API
)

router = APIRouter(prefix='/users', tags=['users'])

# Получение всех пользователей
@router.get('/', response_model=list[UserResponse])
async def all_users(db: Annotated[Session, Depends(get_db)]):
    users = db.scalars(select(User)).all()
    return users

# Получение пользователя по ID
@router.get('/{user_id}', response_model=UserResponse)
async def user_by_id(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")

    return user

# Создание нового пользователя
@router.post('/create', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: CreateUser, db: Annotated[Session, Depends(get_db)]):
    try:
        slug = slugify(user.username)
        existing_user = db.scalar(select(User).where(User.username == user.username))
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )

        new_user = User(
            username=user.username,
            firstname=user.firstname,
            lastname=user.lastname,
            age=user.age,
            slug=slug
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user  # Возвращаем ORM объект

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        ) from e


# Обновление пользователя
@router.put('/update/{user_id}', response_model=CreateUser)
async def update_user(user_id: int, user: UpdateUser, db: Annotated[Session, Depends(get_db)]):
    try:
        # Проверяем существование пользователя
        existing_user = db.scalar(select(User).where(User.id == user_id))
        if existing_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User was not found"
            )

        # Создаем словарь со значениями для обновления
        update_data = user.model_dump(exclude_unset=True)  # Исключаем поля со значением None
        if 'username' in update_data:
            update_data['slug'] = slugify(update_data['username'])

        # Обновляем пользователя
        stmt = update(User).where(User.id == user_id).values(**update_data)
        db.execute(stmt)
        db.commit()

        # Возвращаем обновленного пользователя
        updated_user = db.scalar(select(User).where(User.id == user_id))
        return updated_user
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        ) from e

# Удаление пользователя
@router.delete('/delete/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    try:
        # Проверяем существование пользователя
        existing_user = db.scalar(select(User).where(User.id == user_id))
        if existing_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User was not found"
            )

        # Удаляем пользователя
        stmt = delete(User).where(User.id == user_id)
        db.execute(stmt)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        ) from e

# Подключаем роутер к приложению
app.include_router(router)

# Запуск приложения
if __name__ == "__main__":
    import sys
    import os

    # Добавляем родительскую директорию в PYTHONPATH
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
