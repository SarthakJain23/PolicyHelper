import logging
import uuid
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.services.rag.workflow.stream import get_chat_stream_service

logger = logging.getLogger(__name__)


async def stream_rag_chat(
    session_id: uuid.UUID,
    user_message_content: str,
    current_user: User,
    db: AsyncSession,
    model_name: str | None = None,
    provider_name: str | None = None,
) -> AsyncGenerator[str, None]:
    """
    Public entrypoint for streaming chat responses.
    Dispatches to the singleton ChatStreamService instance.
    """
    service = get_chat_stream_service()
    async for event_line in service.stream_chat(
        session_id=session_id,
        user_message_content=user_message_content,
        current_user=current_user,
        db=db,
        model_name=model_name,
        provider_name=provider_name,
    ):
        yield event_line
