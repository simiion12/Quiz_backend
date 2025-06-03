from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from typing import List

from src.database.database import get_async_session
from src.models.models import Course
from src.schemas.course_schemas import CourseCreate, Course as CourseSchema

router = APIRouter(prefix="/courses", tags=["courses"])

@router.post("/", response_model=CourseSchema)
async def create_course(course: CourseCreate, db: AsyncSession = Depends(get_async_session)):
    query = select(Course).where(Course.name == course.name)
    result = await db.execute(query)
    db_course = result.scalar_one_or_none()

    if db_course:
        raise HTTPException(status_code=400, detail="This course name already registered")

    db_course = Course(
        name=course.name,
        start_date=course.start_date,
        end_date=course.end_date,
        people_count=course.people_count,
    )

    db.add(db_course)
    await db.commit()
    await db.refresh(db_course)
    return db_course


@router.get("/", response_model=List[CourseSchema])
async def get_courses(db: AsyncSession = Depends(get_async_session), skip: int = 0, limit: int = 100):
    query = select(Course).offset(skip).limit(limit)
    result = await db.execute(query)
    courses = result.scalars().all()
    return courses


@router.get("/{id}", response_model=CourseSchema)
async def get_course(course_id: int, db: AsyncSession = Depends(get_async_session)):
    query = select(Course).where(Course.id == course_id)
    result = await db.execute(query)
    db_course = result.scalar_one_or_none()

    if db_course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return db_course


@router.put("/{id}", response_model=CourseSchema)
async def update_course(course_id: int, course: CourseCreate, db: AsyncSession = Depends(get_async_session)):
    query = select(Course).where(Course.id == course_id)
    result = await db.execute(query)
    db_user = result.scalar_one_or_none()

    if db_user is None:
        raise HTTPException(status_code=404, detail="Course not found")

    stmt = (
        update(Course)
        .where(Course.id == course_id)
        .values(**course.dict(exclude_unset=True))
    )
    await db.execute(stmt)
    await db.commit()

    result = await db.execute(query)
    updated_course = result.scalar_one()
    return updated_course


@router.delete("/{id}")
async def delete_course(course_id: int, db: AsyncSession = Depends(get_async_session)):
    query = select(Course).where(Course.id == course_id)
    result = await db.execute(query)
    db_course = result.scalar_one_or_none()

    if db_course is None:
        raise HTTPException(status_code=404, detail="Course not found")

    stmt = delete(Course).where(Course.id == course_id)
    await db.execute(stmt)
    await db.commit()

    return {"message": f"Course with id: {course_id}, deleted"}