import logging
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings

from app.core.crypto import decrypt_api_key
from app.models.organization import OrganizationLLMConfig, Organization
from app.services.llm.base import LLMProviderService
from app.services.llm.openai import OpenAIProvider
from app.services.llm.anthropic import AnthropicProvider
from app.services.llm.gemini import GeminiProvider
from app.services.llm.decision_agent import LLMDecisionAgent

logger = logging.getLogger(__name__)


class LLMProviderFactory:
    """
    Factory to return configured LLM and Embeddings providers dynamically
    from database-backed organization settings.
    """

    @staticmethod
    def _create_provider_instance(
        provider: str,
        api_key: str,
        base_url: str | None = None,
    ) -> LLMProviderService:
        if not api_key:
            raise ValueError(f"api_key is required to instantiate {provider} provider.")
        p = provider.lower()
        if p == "anthropic":
            return AnthropicProvider(api_key=api_key, base_url=base_url)
        elif p in ["gemini", "google"]:
            return GeminiProvider(api_key=api_key)
        else:
            return OpenAIProvider(api_key=api_key, base_url=base_url)

    @classmethod
    async def get_active_configs(
        cls, db: AsyncSession, org_id: uuid.UUID | None = None
    ) -> list[OrganizationLLMConfig]:
        """Retrieve active LLM configurations from the database."""
        stmt = select(OrganizationLLMConfig).where(OrganizationLLMConfig.is_active == True)
        if org_id:
            stmt = stmt.where(OrganizationLLMConfig.organization_id == org_id)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @classmethod
    async def get_chat_model(
        cls,
        db: AsyncSession,
        provider_name: str | None = None,
        model_name: str | None = None,
        temperature: float = 0.1,
        streaming: bool = True,
    ) -> BaseChatModel:
        """
        Dynamically instantiate a ChatModel based on user-selected provider and model,
        resolving encrypted keys stored in the database.
        """
        configs = await cls.get_active_configs(db)
        if not configs:
            raise RuntimeError(
                "No active LLM provider configured in the database. "
                "Please configure an LLM provider (OpenAI, Anthropic, or Gemini) in the Settings page."
            )

        config_map = {c.provider.lower(): c for c in configs}

        # If provider is not specified, infer from model name
        target_provider = (provider_name or "").lower()
        if not target_provider and model_name:
            if "claude" in model_name.lower():
                target_provider = "anthropic"
            elif "gemini" in model_name.lower():
                target_provider = "gemini"
            else:
                target_provider = "openai"

        # Fallback to the first active configured provider if requested provider not found
        cfg = config_map.get(target_provider) or configs[0]
        api_key = decrypt_api_key(cfg.encrypted_api_key)
        provider = cls._create_provider_instance(cfg.provider, api_key, cfg.base_url)
        return provider.get_chat_model(
            model_name=model_name, temperature=temperature, streaming=streaming
        )

    @classmethod
    async def get_fast_model(
        cls, db: AsyncSession, temperature: float = 0.3
    ) -> BaseChatModel:
        """Use the LangChain decision agent to pick the optimal fast model."""
        active_configs = await cls.get_active_configs(db)
        return LLMDecisionAgent.select_fast_model(active_configs, temperature=temperature)

    @classmethod
    async def get_embeddings(
        cls,
        db: AsyncSession,
        custom_model: str | None = None,
        custom_dimensions: int | None = None,
    ) -> Embeddings:
        """Use the LangChain decision agent to resolve the active Embeddings model."""
        active_configs = await cls.get_active_configs(db)
        return LLMDecisionAgent.select_embeddings_model(
            active_configs,
            custom_model=custom_model,
            custom_dimensions=custom_dimensions,
        )

