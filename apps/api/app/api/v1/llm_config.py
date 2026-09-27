from datetime import datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.core.crypto import CryptoService
from app.models.user import User
from app.models.organization import Organization, OrganizationLLMConfig
from app.schemas.role import UserRole
from app.schemas.llm_config import (
    TestAndDiscoverRequest,
    TestAndDiscoverResponse,
    LLMConfigSaveRequest,
    LLMConfigResponse,
    OrganizationModelsResponse,
    DiscoveredModel,
    DiscoveredEmbeddingModel,
    ReindexRequest,
    ReindexStatusResponse,
)
from app.services.llm.discovery import ModelDiscoveryService
from app.services.ingestion.reindex import ReindexService

router = APIRouter(prefix="/llm-config", tags=["LLM Provider Configuration"])


@router.get(
    "",
    response_model=list[LLMConfigResponse],
    dependencies=[Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.HR_ADMIN]))],
)
async def list_llm_configs(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List all saved LLM configurations with masked key fingerprints for the admin."""
    stmt = (
        select(OrganizationLLMConfig)
        .order_by(OrganizationLLMConfig.is_active.desc(), OrganizationLLMConfig.created_at.desc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post(
    "/test-and-discover",
    response_model=TestAndDiscoverResponse,
    dependencies=[Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.HR_ADMIN]))],
)
async def test_and_discover_models(
    payload: TestAndDiscoverRequest,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Test an API key against the specified LLM vendor (OpenAI, Anthropic, Gemini)
    and dynamically return all compatible chat and embedding models.
    """
    discovery = ModelDiscoveryService.get_instance()
    try:
        data = await discovery.get_models(
            provider=payload.provider,
            api_key=payload.api_key.strip(),
            base_url=payload.base_url,
        )

        chat_models = [
            DiscoveredModel(
                id=m["id"],
                name=m.get("name", m["id"]),
                category=m.get("category", "flagship"),
            )
            for m in data.get("chat_models", [])
        ]
        embedding_models = [
            DiscoveredEmbeddingModel(
                id=m["id"],
                name=m.get("name", m["id"]),
                dimensions=m.get("dimensions", 1536),
            )
            for m in data.get("embedding_models", [])
        ]

        default_chat = chat_models[0].id if chat_models else None
        default_emb = embedding_models[0].id if embedding_models else None

        return TestAndDiscoverResponse(
            valid=True,
            chat_models=chat_models,
            embedding_models=embedding_models,
            default_chat_model=default_chat,
            default_embedding_model=default_emb,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to validate {payload.provider} credentials or fetch models: {str(e)}",
        )


@router.post(
    "",
    response_model=LLMConfigResponse,
    dependencies=[Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.HR_ADMIN]))],
)
async def save_llm_config(
    payload: LLMConfigSaveRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Save or update encrypted LLM provider configuration at the organization level."""
    # 1. Fetch organization
    org_stmt = select(Organization).order_by(Organization.created_at).limit(1)
    org = (await db.execute(org_stmt)).scalar_one_or_none()
    if not org:
        org = Organization(name="Default Organization", slug="default", is_active=True)
        db.add(org)
        await db.flush()

    crypto = CryptoService.get_instance()
    encrypted_key = crypto.encrypt(payload.api_key.strip())
    fingerprint = crypto.mask(payload.api_key.strip())

    # Check for existing config for this org & provider
    stmt = select(OrganizationLLMConfig).where(
        OrganizationLLMConfig.organization_id == org.id,
        OrganizationLLMConfig.provider == payload.provider.lower(),
    )
    existing_cfg = (await db.execute(stmt)).scalar_one_or_none()

    if existing_cfg:
        existing_cfg.encrypted_api_key = encrypted_key
        existing_cfg.key_fingerprint = fingerprint
        existing_cfg.base_url = payload.base_url
        existing_cfg.default_embedding_model = payload.default_embedding_model
        existing_cfg.embedding_dimensions = payload.embedding_dimensions
        existing_cfg.is_active = payload.is_active
        existing_cfg.last_tested_at = datetime.now(timezone.utc)
        config_record = existing_cfg
    else:
        config_record = OrganizationLLMConfig(
            organization_id=org.id,
            provider=payload.provider.lower(),
            encrypted_api_key=encrypted_key,
            key_fingerprint=fingerprint,
            base_url=payload.base_url,
            default_embedding_model=payload.default_embedding_model,
            embedding_dimensions=payload.embedding_dimensions,
            is_active=payload.is_active,
            last_tested_at=datetime.now(timezone.utc),
        )
        db.add(config_record)

    await db.commit()
    await db.refresh(config_record)

    # Invalidate cached discovery models for this provider
    ModelDiscoveryService.get_instance().clear_cache(payload.provider)

    return config_record


@router.get("/models", response_model=OrganizationModelsResponse)
async def get_available_chat_models(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    End-user endpoint:
    Dynamically returns the list of active chat models from the organization's LLM provider.
    """
    stmt = (
        select(OrganizationLLMConfig)
        .where(OrganizationLLMConfig.is_active == True)
        .order_by(OrganizationLLMConfig.updated_at.desc())
    )
    result = await db.execute(stmt)
    configs = result.scalars().all()

    if not configs:
        # Fallback to OpenAI default models
        return OrganizationModelsResponse(
            provider="openai",
            chat_models=[
                DiscoveredModel(id="gpt-4o", name="GPT-4o (Omni)", category="flagship"),
                DiscoveredModel(id="gpt-4o-mini", name="GPT-4o Mini (Fast)", category="fast"),
            ],
            default_model="gpt-4o",
        )

    # Pick the primary active configuration
    active_cfg = configs[0]
    crypto = CryptoService.get_instance()
    plain_key = crypto.decrypt(active_cfg.encrypted_api_key)

    discovery = ModelDiscoveryService.get_instance()
    models_data = await discovery.get_models(
        provider=active_cfg.provider,
        api_key=plain_key,
        base_url=active_cfg.base_url,
    )

    chat_models = [
        DiscoveredModel(
            id=m["id"],
            name=m.get("name", m["id"]),
            category=m.get("category", "flagship"),
        )
        for m in models_data.get("chat_models", [])
    ]

    default_model = chat_models[0].id if chat_models else "gpt-4o"

    return OrganizationModelsResponse(
        provider=active_cfg.provider,
        chat_models=chat_models,
        default_model=default_model,
    )


@router.post(
    "/reindex",
    response_model=ReindexStatusResponse,
    dependencies=[Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.HR_ADMIN]))],
)
async def trigger_reindexing(
    payload: ReindexRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Trigger asynchronous background re-indexing of all document chunks
    when switching embedding models.
    """
    org_stmt = select(Organization).order_by(Organization.created_at).limit(1)
    org = (await db.execute(org_stmt)).scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    reindex_service = ReindexService.get_instance()
    task_id = await reindex_service.start_reindexing(
        org_id=org.id,
        new_embedding_model=payload.new_embedding_model,
        dimensions=payload.dimensions,
    )

    task_data = reindex_service.get_task_status(task_id)
    return ReindexStatusResponse(**task_data)


@router.get(
    "/reindex/{task_id}",
    response_model=ReindexStatusResponse,
    dependencies=[Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.HR_ADMIN]))],
)
async def get_reindex_status(
    task_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Check the real-time progress of an ongoing re-indexing task."""
    task_data = ReindexService.get_instance().get_task_status(task_id)
    if not task_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reindexing task '{task_id}' not found",
        )
    return ReindexStatusResponse(**task_data)
