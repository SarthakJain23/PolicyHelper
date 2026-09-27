import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_user, extract_user_roles, is_admin_user
from app.models.user import User
from app.models.audit import AuditLog
from app.schemas.audit import AuditLogResponse

router = APIRouter(prefix="/logs", tags=["Activity Logs"])


@router.get("", response_model=list[AuditLogResponse])
async def list_activity_logs(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: uuid.UUID | None = None,
    action: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """
    List user activity and system audit logs.
    - Standard employees only see their own activity logs.
    - Admins/HR can see all logs or filter by specific user_id.
    """
    user_roles = extract_user_roles(current_user)
    is_admin = is_admin_user(current_user)

    stmt = (
        select(AuditLog)
        .options(selectinload(AuditLog.user))
        .order_by(AuditLog.created_at.desc())
    )

    if not is_admin:
        # Standard user: only own logs
        stmt = stmt.where(AuditLog.user_id == current_user.id)
    else:
        # Admin: optional filter by target user_id
        if user_id:
            stmt = stmt.where(AuditLog.user_id == user_id)

    if action:
        stmt = stmt.where(AuditLog.action == action.upper())

    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    logs = result.scalars().all()

    response: list[AuditLogResponse] = []
    for log in logs:
        user_email = log.user.email if log.user else None
        user_name = log.user.full_name if log.user else None
        response.append(
            AuditLogResponse(
                id=log.id,
                user_id=log.user_id,
                user_email=user_email,
                user_name=user_name,
                action=log.action,
                ip_address=log.ip_address,
                details=log.details or {},
                created_at=log.created_at,
            )
        )

    return response
