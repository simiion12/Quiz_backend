from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class GradeBase(BaseModel):
    course_id: int
    user_id: int
    grade: float
    quiz_number: int
    date: datetime
    time_completion: float

    model_config = ConfigDict(from_attributes=True)



class GradeCreate(GradeBase):
    pass


class GradeUpdate(GradeBase):
    course_id: Optional[int]
    user_id: Optional[int]
    grade: Optional[float]
    quiz_number: Optional[int]
    date: Optional[datetime]
    time_completion: Optional[float]


class Grade(GradeBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
