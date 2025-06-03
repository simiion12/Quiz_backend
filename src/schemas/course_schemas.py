from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CourseBase(BaseModel):
    name: str
    start_date: date
    end_date: date
    people_count: int

    model_config = ConfigDict(from_attributes=True)


class CourseCreate(CourseBase):
    pass


class CourseUpdate(CourseBase):
    name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    people_count: Optional[int] = None


class Course(CourseBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
