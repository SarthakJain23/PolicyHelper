import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class MessageCitationResponse(BaseModel):
    id: uuid.UUID
    chunk_id: uuid.UUID | None
    document_id: uuid.UUID
    document_title: str
    page_number: int | None
    snippet: str
    relevance_score: float | None

    class Config:
        from_attributes = True


class ChatMessageResponse(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    sender: str
    content: str
    prompt_tokens: int
    completion_tokens: int
    metadata_: dict = Field(alias="metadata")
    created_at: datetime
    citations: list[MessageCitationResponse] = []

    class Config:
        from_attributes = True
        populate_by_name = True


class ChatSessionCreate(BaseModel):
    title: str | None = "New Conversation"


class ChatSessionUpdate(BaseModel):
    title: str | None = None
    is_pinned: bool | None = None
    is_archived: bool | None = None


class ChatSessionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    selected_model: str | None = None
    message_count: int
    is_title_auto_generated: bool
    is_pinned: bool
    is_archived: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatSessionDetailResponse(ChatSessionResponse):
    messages: list[ChatMessageResponse] = []


class ChatStreamRequest(BaseModel):
    content: str = Field(..., min_length=1)
    model: str | None = None
    provider: str | None = None

