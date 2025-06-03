from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    name: str
    surname: str
    email: str
    username: str
    course_id: int
    telegram_id: int = Field(..., ge=0, lt=2 ** 63)

    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[str] = None
    username: Optional[str] = None
    course_id: Optional[int] = None
    telegram_id: Optional[int] = Field(None, ge=0, lt=2 ** 63)


class User(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)