# src/schemas/auth_schemas.py
from pydantic import BaseModel, EmailStr, ConfigDict
from fastapi_users import schemas
from typing import Optional


class UserRead(schemas.BaseUser[int]):
    """Schema for reading user data."""
    id: int
    name: str
    surname: str
    email: EmailStr
    username: str
    telegram_id: int
    course_id: int
    role: str
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    model_config = ConfigDict(from_attributes=True)


class UserCreate(schemas.BaseUserCreate):
    """Schema for creating a new user."""
    name: str
    surname: str
    email: EmailStr
    username: str
    password: str
    telegram_id: int
    course_id: int
    role: str = "student"
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False


class UserUpdate(schemas.BaseUserUpdate):
    """Schema for updating user data."""
    name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    telegram_id: Optional[int] = None
    course_id: Optional[int] = None
    role: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    is_verified: Optional[bool] = None


# Custom login request with remember_me functionality
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False

    model_config = ConfigDict(from_attributes=True)


# Keep for backward compatibility if needed
class UserResponse(UserRead):
    """Alias for UserRead for backward compatibility."""
    pass