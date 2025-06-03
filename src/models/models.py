from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Date, BigInteger
from sqlalchemy.orm import relationship, declarative_base
from fastapi_users.db import SQLAlchemyBaseUserTable


Base = declarative_base()

class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, nullable=False)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    username = Column(String, nullable=False, unique=True)
    course_id = Column(Integer, ForeignKey('course.id'))
    role = Column(String, nullable=False, default="student")  # 'student' or 'admin'

    course = relationship("Course", back_populates="users")
    grades = relationship("Grade", back_populates="user")


class Course(Base):
    __tablename__ = 'course'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    people_count = Column(Integer, nullable=False)

    users = relationship("User", back_populates="course")
    grades = relationship("Grade", back_populates="course")


class Grade(Base):
    __tablename__ = 'grade'

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey('course.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    grade = Column(Float, nullable=False)
    quiz_number = Column(Integer, nullable=False)
    date = Column(DateTime, nullable=False, default=datetime.utcnow)
    time_completion = Column(Float, nullable=False)

    course = relationship("Course", back_populates="grades")
    user = relationship("User", back_populates="grades")
