import os
from typing import Optional
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin, FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    CookieTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv

from src.database.database import get_async_session
from src.models.models import User

load_dotenv()

# Constants
SECRET = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ACCESS_TOKEN_EXPIRE_SECONDS = 3600  # 1 hour


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    """User manager for handling user operations."""
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"✅ User {user.email} (ID: {user.id}) has registered.")

    async def on_after_login(self, user: User, request: Optional[Request] = None):
        print(f"🔐 User {user.email} (ID: {user.id}) logged in.")

    async def on_after_logout(self, user: User, request: Optional[Request] = None):
        print(f"🚪 User {user.email} (ID: {user.id}) logged out.")


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    """Get user database instance."""
    yield SQLAlchemyUserDatabase(session, User)


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    """Get user manager instance."""
    yield UserManager(user_db)


def get_jwt_strategy() -> JWTStrategy:
    """Get JWT strategy for authentication."""
    return JWTStrategy(secret=SECRET, lifetime_seconds=ACCESS_TOKEN_EXPIRE_SECONDS)


# Cookie transport configuration (following official docs)
cookie_transport = CookieTransport(
    cookie_max_age=ACCESS_TOKEN_EXPIRE_SECONDS,
    cookie_name="auth_token",
    cookie_httponly=True,
    cookie_samesite="lax"
)

# Authentication backend
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

# FastAPI Users instance
fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend]
)

# Dependencies to get current user
current_active_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)