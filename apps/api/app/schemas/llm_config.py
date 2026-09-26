import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class DiscoveredModel(BaseModel):
    id: str
    name: str
    category: str | None = "flagship"  # 'flagship', 'fast', 'reasoning'


class DiscoveredEmbeddingModel(BaseModel):
    id: str
    name: str
    dimensions: int = 1536


class TestAndDiscoverRequest(BaseModel):
    provider: str = Field(..., description="Provider name: openai, anthropic, or gemini")
    api_key: str = Field(..., min_length=5, description="Plaintext API key to test")
    base_url: str | None = None


class TestAndDiscoverResponse(BaseModel):
    valid: bool
    chat_models: list[DiscoveredModel]
    embedding_models: list[DiscoveredEmbeddingModel]
    default_chat_model: str | None = None
    default_embedding_model: str | None = None


class LLMConfigSaveRequest(BaseModel):
    organization_id: uuid.UUID | None = None
    provider: str = Field(..., description="Provider name: openai, anthropic, or gemini")
    api_key: str = Field(..., min_length=5, description="API key to encrypt and save")
    base_url: str | None = None
    default_embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    is_active: bool = True


class LLMConfigResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    provider: str
    key_fingerprint: str
    base_url: str | None
    default_embedding_model: str
    embedding_dimensions: int
    is_active: bool
    last_tested_at: datetime | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrganizationModelsResponse(BaseModel):
    provider: str
    chat_models: list[DiscoveredModel]
    default_model: str


class ReindexRequest(BaseModel):
    new_embedding_model: str
    dimensions: int = 1536


class ReindexStatusResponse(BaseModel):
    task_id: str
    organization_id: str
    status: str  # 'IN_PROGRESS', 'COMPLETED', 'FAILED'
    new_embedding_model: str
    total_chunks: int
    completed_chunks: int
    progress_percentage: float
    error: str | None
    started_at: str
    completed_at: str | None
