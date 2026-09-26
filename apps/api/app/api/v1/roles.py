from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.role import Role
from app.models.user import User
from app.schemas.role import RoleResponse

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.get("", response_model=list[RoleResponse])
async def list_roles(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List all available system roles."""
    stmt = select(Role).order_by(Role.name)
    result = await db.execute(stmt)
    return result.scalars().all()
