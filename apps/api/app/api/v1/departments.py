import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.models.department import Department
from app.models.user import User
from app.models.audit import AuditLog
from app.schemas.role import UserRole
from app.schemas.department import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse,
)

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.get("", response_model=list[DepartmentResponse])
async def list_departments(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    include_inactive: bool = False,
):
    """List all departments."""
    stmt = select(Department)
    if not include_inactive:
        stmt = stmt.where(Department.is_active == True)
    stmt = stmt.order_by(Department.name)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
async def create_department(
    dept_data: DepartmentCreate,
    current_user: Annotated[User, Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.HR_ADMIN]))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create a new department (Admin/HR only)."""
    # Check duplicate name or code
    stmt = select(Department).where(
        (Department.name.ilike(dept_data.name.strip()))
        | (Department.code.ilike(dept_data.code.strip().upper()))
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A department with this name or code already exists",
        )

    dept = Department(
        name=dept_data.name.strip(),
        code=dept_data.code.strip().upper(),
        description=dept_data.description,
        is_active=dept_data.is_active,
    )
    db.add(dept)

    audit_entry = AuditLog(
        user_id=current_user.id,
        action="CREATE_DEPARTMENT",
        details={"name": dept.name, "code": dept.code},
    )
    db.add(audit_entry)

    await db.commit()
    await db.refresh(dept)
    return dept


@router.get("/{dept_id}", response_model=DepartmentResponse)
async def get_department(
    dept_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get department details by ID."""
    dept = await db.get(Department, dept_id)
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found",
        )
    return dept


@router.put("/{dept_id}", response_model=DepartmentResponse)
async def update_department(
    dept_id: uuid.UUID,
    dept_data: DepartmentUpdate,
    current_user: Annotated[User, Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.HR_ADMIN]))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update department details (Admin/HR only)."""
    dept = await db.get(Department, dept_id)
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found",
        )

    if dept_data.name is not None:
        # Check duplicate name
        stmt = select(Department).where(
            Department.name.ilike(dept_data.name.strip()),
            Department.id != dept_id,
        )
        if (await db.execute(stmt)).scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Department name already in use",
            )
        dept.name = dept_data.name.strip()

    if dept_data.code is not None:
        # Check duplicate code
        stmt = select(Department).where(
            Department.code.ilike(dept_data.code.strip().upper()),
            Department.id != dept_id,
        )
        if (await db.execute(stmt)).scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Department code already in use",
            )
        dept.code = dept_data.code.strip().upper()

    if dept_data.description is not None:
        dept.description = dept_data.description

    if dept_data.is_active is not None:
        dept.is_active = dept_data.is_active

    audit_entry = AuditLog(
        user_id=current_user.id,
        action="UPDATE_DEPARTMENT",
        details={"dept_id": str(dept_id), "name": dept.name},
    )
    db.add(audit_entry)

    await db.commit()
    await db.refresh(dept)
    return dept


@router.delete("/{dept_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(
    dept_id: uuid.UUID,
    current_user: Annotated[User, Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.HR_ADMIN]))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Soft delete / deactivate a department."""
    dept = await db.get(Department, dept_id)
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found",
        )

    dept.is_active = False
    audit_entry = AuditLog(
        user_id=current_user.id,
        action="DEACTIVATE_DEPARTMENT",
        details={"dept_id": str(dept_id), "name": dept.name},
    )
    db.add(audit_entry)

    await db.commit()
    return None
