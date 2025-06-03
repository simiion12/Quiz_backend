from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from typing import List

from src.database.database import get_async_session
from src.models.models import User
from src.schemas.user_schemas import UserCreate, User as UserSchema

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserSchema)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_async_session)):
    query = select(User).where(User.username == user.username)
    result = await db.execute(query)
    db_user = result.scalar_one_or_none()

    if db_user:
        raise HTTPException(status_code=400, detail="This telegram account already registered")

    db_user = User(
        telegram_id=user.telegram_id,
        name=user.name,
        surname=user.surname,
        email=user.email,
        username=user.username,
        course_id=user.course_id
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.get("/", response_model=List[UserSchema])
async def get_users(db: AsyncSession = Depends(get_async_session), skip: int = 0, limit: int = 100):
    query = select(User).offset(skip).limit(limit)
    result = await db.execute(query)
    users = result.scalars().all()
    return users


@router.get("/{telegram_id}", response_model=UserSchema)
async def get_user(telegram_id: int, db: AsyncSession = Depends(get_async_session)):
    query = select(User).where(User.telegram_id == telegram_id)
    result = await db.execute(query)
    db_user = result.scalar_one_or_none()

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.put("/{telegram_id}", response_model=UserSchema)
async def update_user(telegram_id: int, user: UserCreate, db: AsyncSession = Depends(get_async_session)):
    query = select(User).where(User.telegram_id == telegram_id)
    result = await db.execute(query)
    db_user = result.scalar_one_or_none()

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    stmt = (
        update(User)
        .where(User.telegram_id == telegram_id)
        .values(**user.dict(exclude_unset=True))
    )
    await db.execute(stmt)
    await db.commit()

    result = await db.execute(query)
    updated_user = result.scalar_one()
    return updated_user


@router.delete("/{telegram_id}")
async def delete_user(telegram_id: int, db: AsyncSession = Depends(get_async_session)):
    query = select(User).where(User.telegram_id == telegram_id)
    result = await db.execute(query)
    db_user = result.scalar_one_or_none()

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    stmt = delete(User).where(User.telegram_id == telegram_id)
    await db.execute(stmt)
    await db.commit()

    return {"message": f"User with id: {telegram_id}, deleted"}