import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.models.user import User
from app.models.organization import Organization
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
)

router = APIRouter(prefix="/organization", tags=["Organization Management"])


@router.get("", response_model=OrganizationResponse)
async def get_organization(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Retrieve the primary organization details."""
    stmt = select(Organization).order_by(Organization.created_at).limit(1)
    result = await db.execute(stmt)
    org = result.scalar_one_or_none()

    if not org:
        # Auto-create default organization if missing
        org = Organization(
            name="My Organization",
            slug="default",
            is_active=True,
        )
        db.add(org)
        await db.commit()
        await db.refresh(org)

    return org


@router.put(
    "",
    response_model=OrganizationResponse,
    dependencies=[Depends(require_roles(["SUPER_ADMIN", "HR_ADMIN"]))],
)
async def update_organization(
    payload: OrganizationUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update organization settings (Super Admin / HR Admin only)."""
    stmt = select(Organization).order_by(Organization.created_at).limit(1)
    result = await db.execute(stmt)
    org = result.scalar_one_or_none()

    if not org:
        org = Organization(
            name=payload.name or "My Organization",
            slug=payload.slug or "default",
            is_active=True if payload.is_active is None else payload.is_active,
        )
        db.add(org)
    else:
        if payload.name is not None:
            org.name = payload.name.strip()
        if payload.slug is not None:
            org.slug = payload.slug.strip().lower()
        if payload.is_active is not None:
            org.is_active = payload.is_active

    await db.commit()
    await db.refresh(org)
    return org
