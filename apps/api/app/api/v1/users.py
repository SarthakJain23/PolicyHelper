import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import (
    get_current_user,
    require_roles,
    get_password_hash,
    generate_random_password,
)
from app.models.user import User
from app.models.role import Role
from app.models.department import Department
from app.models.audit import AuditLog
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserCreatedWithPasswordResponse,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=list[UserResponse])
async def list_users(
    current_user: Annotated[User, Depends(require_roles(["SUPER_ADMIN", "HR_ADMIN"]))],
    db: Annotated[AsyncSession, Depends(get_db)],
    department_id: uuid.UUID | None = None,
    role_name: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List all users with roles and department (Admin/HR only)."""
    stmt = (
        select(User)
        .options(selectinload(User.roles), selectinload(User.department))
        .order_by(User.created_at.desc())
    )
    if department_id:
        stmt = stmt.where(User.department_id == department_id)

    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    users = result.scalars().all()

    if role_name:
        users = [u for u in users if any(r.name == role_name for r in u.roles)]

    return users


@router.post("", response_model=UserCreatedWithPasswordResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: Annotated[User, Depends(require_roles(["SUPER_ADMIN", "HR_ADMIN"]))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Create a new user with an auto-generated temporary password.
    User will be required to change their password upon first login (must_change_password=True).
    """
    email_clean = user_data.email.lower().strip()

    # Check if email exists
    stmt = select(User).where(User.email == email_clean)
    if (await db.execute(stmt)).scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists",
        )

    # Validate department
    if user_data.department_id:
        dept = await db.get(Department, user_data.department_id)
        if not dept or not dept.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Selected department does not exist or is inactive",
            )

    # Fetch roles
    roles_stmt = select(Role).where(Role.name.in_(user_data.role_names))
    roles = (await db.execute(roles_stmt)).scalars().all()
    if not roles:
        # Fallback to EMPLOYEE
        default_role_stmt = select(Role).where(Role.name == "EMPLOYEE")
        roles = (await db.execute(default_role_stmt)).scalars().all()

    # Generate secure random temporary password
    temporary_password = generate_random_password(12)
    password_hash = get_password_hash(temporary_password)

    new_user = User(
        email=email_clean,
        full_name=user_data.full_name.strip(),
        password_hash=password_hash,
        department_id=user_data.department_id,
        is_active=True,
        must_change_password=True,
        roles=list(roles),
    )
    db.add(new_user)

    audit_entry = AuditLog(
        user_id=current_user.id,
        action="CREATE_USER",
        details={"created_email": new_user.email, "roles": [r.name for r in roles]},
    )
    db.add(audit_entry)

    await db.commit()

    # Re-fetch user with relationships
    stmt = (
        select(User)
        .options(selectinload(User.roles), selectinload(User.department))
        .where(User.id == new_user.id)
    )
    user_with_rel = (await db.execute(stmt)).scalar_one()

    return UserCreatedWithPasswordResponse(
        user=user_with_rel,
        temporary_password=temporary_password,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: uuid.UUID,
    current_user: Annotated[User, Depends(require_roles(["SUPER_ADMIN", "HR_ADMIN"]))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get single user profile by ID."""
    stmt = (
        select(User)
        .options(selectinload(User.roles), selectinload(User.department))
        .where(User.id == user_id)
    )
    user = (await db.execute(stmt)).scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: uuid.UUID,
    user_data: UserUpdate,
    current_user: Annotated[User, Depends(require_roles(["SUPER_ADMIN", "HR_ADMIN"]))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update user profile, roles, department, or active status (Admin/HR only)."""
    stmt = (
        select(User)
        .options(selectinload(User.roles), selectinload(User.department))
        .where(User.id == user_id)
    )
    user = (await db.execute(stmt)).scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user_data.full_name is not None:
        user.full_name = user_data.full_name.strip()

    if user_data.department_id is not None:
        dept = await db.get(Department, user_data.department_id)
        if not dept or not dept.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Selected department does not exist or is inactive",
            )
        user.department_id = user_data.department_id

    if user_data.is_active is not None:
        user.is_active = user_data.is_active

    if user_data.role_names is not None:
        roles_stmt = select(Role).where(Role.name.in_(user_data.role_names))
        roles = (await db.execute(roles_stmt)).scalars().all()
        if roles:
            user.roles = list(roles)

    audit_entry = AuditLog(
        user_id=current_user.id,
        action="UPDATE_USER",
        details={"updated_user_id": str(user_id)},
    )
    db.add(audit_entry)

    await db.commit()
    await db.refresh(user)
    return user


@router.post("/{user_id}/reset-password", response_model=UserCreatedWithPasswordResponse)
async def admin_reset_password(
    user_id: uuid.UUID,
    current_user: Annotated[User, Depends(require_roles(["SUPER_ADMIN", "HR_ADMIN"]))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Regenerate a random temporary password for a user and enforce password reset on next login."""
    stmt = (
        select(User)
        .options(selectinload(User.roles), selectinload(User.department))
        .where(User.id == user_id)
    )
    user = (await db.execute(stmt)).scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    temp_password = generate_random_password(12)
    user.password_hash = get_password_hash(temp_password)
    user.must_change_password = True

    audit_entry = AuditLog(
        user_id=current_user.id,
        action="ADMIN_RESET_PASSWORD",
        details={"target_user_id": str(user_id)},
    )
    db.add(audit_entry)

    await db.commit()
    await db.refresh(user)

    return UserCreatedWithPasswordResponse(
        user=user,
        temporary_password=temp_password,
    )
