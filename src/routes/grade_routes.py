from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from typing import List

from src.database.database import get_async_session
from src.models.models import Grade
from src.schemas.grades_schemas import GradeCreate, Grade as GradeSchema

router = APIRouter(prefix="/grades", tags=["grades"])

@router.post("/", response_model=GradeSchema)
async def create_grade(grade: GradeCreate, db: AsyncSession = Depends(get_async_session)):
    from sqlalchemy import and_
    query = select(Grade).where(
        and_(
            Grade.course_id == grade.course_id,
            Grade.user_id == grade.user_id,
            Grade.quiz_number == grade.quiz_number
        )
    )
    result = await db.execute(query)
    db_grade = result.scalar_one_or_none()

    if db_grade:
        raise HTTPException(status_code=400, detail="Grade for this quiz already registered")

    db_grade = Grade(
        course_id=grade.course_id,
        user_id=grade.user_id,
        grade=grade.grade,
        quiz_number=grade.quiz_number,
        date=grade.date,
        time_completion=grade.time_completion
    )

    db.add(db_grade)
    await db.commit()
    await db.refresh(db_grade)
    return db_grade


@router.get("/course/{course_id}users/{user_id}", response_model=List[int])
async def get_graded_quiz_numbers(course_id: int,user_id: int, db: AsyncSession = Depends(get_async_session)):
    from sqlalchemy import and_

    query = select(Grade.quiz_number).where(
        and_(
            Grade.course_id == course_id,
            Grade.user_id == user_id
        )
    )
    result = await db.execute(query)
    grades = result.scalars().all()
    return grades



@router.get("/my-progress/course/{course_id}users/{user_id}", response_model=List[int])
async def get_grades(course_id: int,user_id: int, db: AsyncSession = Depends(get_async_session)):
    from sqlalchemy import and_

    query = select(Grade).where(
        and_(
            Grade.course_id == course_id,
            Grade.user_id == user_id
        )
    )
    result = await db.execute(query)
    grades = result.scalars().all()
    return grades

@router.get("/{id}", response_model=GradeSchema)
async def get_grade(grade_id: int, db: AsyncSession = Depends(get_async_session)):
    query = select(Grade).where(Grade.id == grade_id)
    result = await db.execute(query)
    db_grade = result.scalar_one_or_none()

    if db_grade is None:
        raise HTTPException(status_code=404, detail="Grade not found")
    return db_grade


@router.put("/{id}", response_model=GradeSchema)
async def update_grade(grade_id: int, grade: GradeCreate, db: AsyncSession = Depends(get_async_session)):
    query = select(Grade).where(Grade.id == grade_id)
    result = await db.execute(query)
    db_grade = result.scalar_one_or_none()

    if db_grade is None:
        raise HTTPException(status_code=404, detail="Grade not found")

    stmt = (
        update(Grade)
        .where(Grade.id == grade_id)
        .values(**grade.dict(exclude_unset=True))
    )
    await db.execute(stmt)
    await db.commit()

    result = await db.execute(query)
    updated_course = result.scalar_one()
    return updated_course


@router.delete("/{id}")
async def delete_grade(grade_id: int, db: AsyncSession = Depends(get_async_session)):
    query = select(Grade).where(Grade.id == grade_id)
    result = await db.execute(query)
    db_grade = result.scalar_one_or_none()

    if db_grade is None:
        raise HTTPException(status_code=404, detail="Grade not found")

    stmt = delete(Grade).where(Grade.id == grade_id)
    await db.execute(stmt)
    await db.commit()

    return {"message": f"Grade with id: {grade_id}, deleted"}