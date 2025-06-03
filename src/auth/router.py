from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.auth.config import (
    auth_backend,
    fastapi_users,
    current_active_user,
    get_user_manager
)
from src.schemas.auth_schemas import UserRead, UserCreate, UserUpdate, LoginRequest
from src.models.models import User
from src.database.database import get_async_session

# Create the main auth router
router = APIRouter(tags=["authentication"])

# Include FastAPI Users standard routes
router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"]
)
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/auth/users",
    tags=["users"],
)


# CORRECT: Use password_helper from UserManager
async def authenticate_with_password_helper(
        email: str,
        password: str,
        db: AsyncSession,
        user_manager
):
    """Authenticate using UserManager's password_helper (the correct way)."""
    try:
        # Get user by email
        query = select(User).where(User.email == email)
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            # Try username if email fails
            query = select(User).where(User.username == email)
            result = await db.execute(query)
            user = result.scalar_one_or_none()

        if not user:
            print(f"❌ User not found: {email}")
            return None

        # CORRECT: Use password_helper from UserManager
        try:
            password_helper = user_manager.password_helper
            verified, updated_password_hash = password_helper.verify_and_update(
                password, user.hashed_password
            )

            if not verified:
                print(f"❌ Invalid password for user: {email}")
                return None

        except Exception as verify_error:
            print(f"❌ Password verification failed: {verify_error}")
            return None

        if not user.is_active:
            print(f"❌ User inactive: {email}")
            return None

        print(f"✅ Authentication successful for: {email}")
        return user

    except Exception as e:
        print(f"❌ Authentication error: {e}")
        import traceback
        traceback.print_exc()
        return None


# Custom login endpoint using password_helper
@router.post("/login")
async def custom_login(
        response: Response,
        request: Request,
        login_data: LoginRequest,
        db: AsyncSession = Depends(get_async_session),
        user_manager=Depends(get_user_manager),
):
    """Custom login using UserManager's password_helper."""

    print(f"🔐 Login attempt for: {login_data.email}")

    # Use password_helper for verification
    user = await authenticate_with_password_helper(
        login_data.email,
        login_data.password,
        db,
        user_manager
    )

    if not user:
        print(f"❌ Authentication failed for: {login_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email/username or password"
        )

    print(f"✅ User authenticated: {user.email} (ID: {user.id})")

    # Generate JWT token using the auth backend
    strategy = auth_backend.get_strategy()
    token = await strategy.write_token(user)

    # Set cookie
    response.set_cookie(
        key="auth_token",
        value=token,
        max_age=3600,  # 1 hour
        httponly=True,
        samesite="lax",
    )

    # Call after login hook
    await user_manager.on_after_login(user, request)

    print(f"🍪 Cookie set for user: {user.email}")

    # Return detailed user information
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "name": user.name,
        "surname": user.surname,
        "role": user.role,
        "email": user.email,
        "course_id": user.course_id,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "is_verified": user.is_verified
    }


# Custom logout endpoint
@router.post("/logout")
async def custom_logout(
        response: Response,
        request: Request,
        current_user: User = Depends(current_active_user),
        user_manager=Depends(get_user_manager),
):
    """Custom logout endpoint."""

    print(f"🚪 Logout for user: {current_user.email}")

    # Clear the cookie
    response.delete_cookie(key="auth_token")

    # Call after logout hook
    await user_manager.on_after_logout(current_user, request)

    return {"message": "Successfully logged out"}


# Debug endpoint to check password_helper
@router.post("/debug-password-helper")
async def debug_password_helper(
        login_data: LoginRequest,
        db: AsyncSession = Depends(get_async_session),
        user_manager=Depends(get_user_manager),
):
    """Debug endpoint to check password_helper functionality."""

    try:
        # Get user
        query = select(User).where(User.email == login_data.email)
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            return {"error": "User not found", "email": login_data.email}

        # Check if password_helper exists
        password_helper = getattr(user_manager, 'password_helper', None)
        if not password_helper:
            return {
                "error": "password_helper not found",
                "user_manager_attributes": [attr for attr in dir(user_manager) if not attr.startswith('_')],
                "user_manager_type": str(type(user_manager))
            }

        # Test password verification with password_helper
        try:
            verified, updated_hash = password_helper.verify_and_update(
                login_data.password,
                user.hashed_password
            )
        except Exception as e:
            return {
                "error": f"Password verification failed: {str(e)}",
                "password_helper_type": str(type(password_helper)),
                "password_helper_methods": [method for method in dir(password_helper) if not method.startswith('_')]
            }

        # Test creating a new hash
        try:
            new_hash = password_helper.hash(login_data.password)
            new_verified, _ = password_helper.verify_and_update(login_data.password, new_hash)
        except Exception as e:
            new_hash = f"Hash creation failed: {str(e)}"
            new_verified = False

        return {
            "user_found": True,
            "user_id": user.id,
            "email": user.email,
            "user_active": user.is_active,
            "password_helper_exists": True,
            "password_helper_type": str(type(password_helper)),
            "stored_hash_preview": user.hashed_password[:30] + "...",
            "password_valid_with_stored": verified,
            "new_hash_preview": str(new_hash)[:30] + "...",
            "password_valid_with_new_hash": new_verified
        }

    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "traceback": traceback.format_exc()
        }


# Test endpoint
@router.get("/test")
async def test_auth(current_user: User = Depends(current_active_user)):
    """Test endpoint to verify authentication."""
    return {
        "message": "Authentication successful!",
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "username": current_user.username,
            "role": current_user.role
        }
    }