from datetime import datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    set_auth_cookies,
    clear_auth_cookies,
    get_current_user,
    extract_user_roles,
)
from app.models.user import User
from app.models.audit import AuditLog
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    ChangePasswordRequest,
)
from app.schemas.user import UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Authenticate user with email and password, setting HttpOnly cookies."""
    stmt = (
        select(User)
        .options(selectinload(User.roles), selectinload(User.department))
        .where(User.email == login_data.email.lower().strip())
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Contact an administrator.",
        )

    user.last_login_at = datetime.now(timezone.utc)
    
    audit_entry = AuditLog(
        user_id=user.id,
        action="LOGIN",
        details={"email": user.email},
    )
    db.add(audit_entry)
    await db.commit()
    await db.refresh(user)

    role_names = extract_user_roles(user)
    dept_id = str(user.department_id) if user.department_id else None
    dept_name = user.department.name if user.department else None

    access_token = create_access_token(
        user_id=str(user.id),
        email=user.email,
        roles=role_names,
        department_id=dept_id,
        must_change_password=user.must_change_password,
    )
    refresh_token = create_refresh_token(user_id=str(user.id), email=user.email)

    set_auth_cookies(response, access_token=access_token, refresh_token=refresh_token)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        roles=role_names,
        department_id=user.department_id,
        department_name=dept_name,
        must_change_password=user.must_change_password,
    )


@router.post("/change-password", response_model=TokenResponse)
async def change_password(
    password_data: ChangePasswordRequest,
    response: Response,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Change password and refresh HttpOnly cookies."""
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    if len(password_data.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters long",
        )

    if password_data.current_password == password_data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password",
        )

    current_user.password_hash = get_password_hash(password_data.new_password)
    current_user.must_change_password = False
    
    # Audit log
    audit_entry = AuditLog(
        user_id=current_user.id,
        action="CHANGE_PASSWORD",
        details={"email": current_user.email},
    )
    db.add(audit_entry)
    await db.commit()
    await db.refresh(current_user)

    role_names = extract_user_roles(current_user)
    dept_id = str(current_user.department_id) if current_user.department_id else None
    dept_name = current_user.department.name if current_user.department else None

    # Issue updated token with must_change_password = False
    access_token = create_access_token(
        user_id=str(current_user.id),
        email=current_user.email,
        roles=role_names,
        department_id=dept_id,
        must_change_password=False,
    )
    refresh_token = create_refresh_token(user_id=str(current_user.id), email=current_user.email)

    set_auth_cookies(response, access_token=access_token, refresh_token=refresh_token)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        roles=role_names,
        department_id=current_user.department_id,
        department_name=dept_name,
        must_change_password=False,
    )


@router.post("/logout")
async def logout(response: Response):
    """Log out by clearing HttpOnly authentication cookies from the backend."""
    clear_auth_cookies(response)
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_my_profile(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Retrieve profile of the currently logged-in user."""
    return current_user
