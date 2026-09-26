import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.chat import ChatSession, ChatMessage
from app.schemas.chat import (
    ChatSessionCreate,
    ChatSessionUpdate,
    ChatSessionResponse,
    ChatSessionDetailResponse,
    ChatStreamRequest,
)
from app.services.rag.graph import stream_rag_chat

router = APIRouter(prefix="/chat", tags=["Chat & Search"])


@router.get("/sessions", response_model=list[ChatSessionResponse])
async def list_chat_sessions(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    include_archived: bool = False,
):
    """List all chat sessions owned by the authenticated employee."""
    stmt = (
        select(ChatSession)
        .where(ChatSession.user_id == current_user.id)
    )
    if not include_archived:
        stmt = stmt.where(ChatSession.is_archived == False)

    stmt = stmt.order_by(ChatSession.is_pinned.desc(), ChatSession.updated_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_chat_session(
    session_data: ChatSessionCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create a new chat conversation session."""
    session = ChatSession(
        user_id=current_user.id,
        title=session_data.title or "New Conversation",
        is_pinned=False,
        is_archived=False,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


@router.get("/sessions/{session_id}", response_model=ChatSessionDetailResponse)
async def get_chat_session(
    session_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Retrieve full chat session turn history with citations."""
    stmt = (
        select(ChatSession)
        .options(
            selectinload(ChatSession.messages).selectinload(ChatMessage.citations)
        )
        .where(ChatSession.id == session_id, ChatSession.user_id == current_user.id)
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found",
        )

    return session


@router.patch("/sessions/{session_id}", response_model=ChatSessionResponse)
async def update_chat_session(
    session_id: uuid.UUID,
    update_data: ChatSessionUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Rename, pin/unpin, or archive/unarchive a chat session."""
    stmt = select(ChatSession).where(
        ChatSession.id == session_id, ChatSession.user_id == current_user.id
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found",
        )

    if update_data.title is not None:
        session.title = update_data.title.strip()
    if update_data.is_pinned is not None:
        session.is_pinned = update_data.is_pinned
    if update_data.is_archived is not None:
        session.is_archived = update_data.is_archived

    await db.commit()
    await db.refresh(session)
    return session


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_session(
    session_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete a chat session and all associated messages and citations."""
    stmt = select(ChatSession).where(
        ChatSession.id == session_id, ChatSession.user_id == current_user.id
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found",
        )

    await db.delete(session)
    await db.commit()
    return None


@router.post("/sessions/{session_id}/stream")
async def stream_chat_response(
    session_id: uuid.UUID,
    request: ChatStreamRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Server-Sent Events (SSE) streaming endpoint:
    - Streams tokens in real-time as LLM produces them
    - Yields citations and automatic session title updates
    - Persists message history and citations in PostgreSQL
    """
    stmt = select(ChatSession).where(
        ChatSession.id == session_id, ChatSession.user_id == current_user.id
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found",
        )

    return StreamingResponse(
        stream_rag_chat(
            session_id=session_id,
            user_message_content=request.content.strip(),
            current_user=current_user,
            db=db,
            model_name=request.model,
            provider_name=request.provider,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
