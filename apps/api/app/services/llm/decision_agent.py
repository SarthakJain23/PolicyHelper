import logging
from typing import Any
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from app.core.crypto import decrypt_api_key
from app.models.organization import OrganizationLLMConfig
from app.services.llm.openai import OpenAIProvider
from app.services.llm.anthropic import AnthropicProvider
from app.services.llm.gemini import GeminiProvider

logger = logging.getLogger(__name__)


class LLMDecisionAgent:
    """
    LangChain Decision Agent that intelligently determines which model to route to
    for background low-latency tasks (titling, query expansion) and embedding generation
    based on active organization credentials and task characteristics.
    """

    @classmethod
    def select_fast_model(
        cls,
        active_configs: list[OrganizationLLMConfig],
        task: str = "title_generation",
        temperature: float = 0.0,
    ) -> BaseChatModel:
        """
        Dynamically decide and instantiate the optimal fast model for low-latency tasks
        like conversation auto-titling and query rewriting.
        """
        # Prioritization strategy for fast, cost-effective background operations:
        # Gemini (Flash) -> OpenAI (Mini) -> Anthropic (Haiku)
        config_map = {cfg.provider.lower(): cfg for cfg in active_configs if cfg.is_active}

        if "gemini" in config_map or "google" in config_map:
            cfg = config_map.get("gemini") or config_map.get("google")
            if not cfg or not cfg.encrypted_api_key:
                raise ValueError("Active Gemini configuration or encrypted API key is missing.")
            api_key = decrypt_api_key(cfg.encrypted_api_key)
            if not api_key:
                raise ValueError("Failed to decrypt API key for Gemini provider.")
            provider = GeminiProvider(api_key=api_key)
            return provider.get_fast_model(model_name="gemini-1.5-flash", temperature=temperature)

        elif "openai" in config_map:
            cfg = config_map["openai"]
            if not cfg or not cfg.encrypted_api_key:
                raise ValueError("Active OpenAI configuration or encrypted API key is missing.")
            api_key = decrypt_api_key(cfg.encrypted_api_key)
            if not api_key:
                raise ValueError("Failed to decrypt API key for OpenAI provider.")
            provider = OpenAIProvider(api_key=api_key, base_url=cfg.base_url)
            return provider.get_fast_model(model_name="gpt-4o-mini", temperature=temperature)

        elif "anthropic" in config_map:
            cfg = config_map["anthropic"]
            if not cfg or not cfg.encrypted_api_key:
                raise ValueError("Active Anthropic configuration or encrypted API key is missing.")
            api_key = decrypt_api_key(cfg.encrypted_api_key)
            if not api_key:
                raise ValueError("Failed to decrypt API key for Anthropic provider.")
            provider = AnthropicProvider(api_key=api_key, base_url=cfg.base_url)
            return provider.get_fast_model(model_name="claude-3-5-haiku-20241022", temperature=temperature)

        raise RuntimeError(
            "No active LLM provider configured in the database. "
            "Please configure your LLM Provider (OpenAI, Anthropic, or Gemini) in the Settings page."
        )

    @classmethod
    def select_embeddings_model(
        cls,
        active_configs: list[OrganizationLLMConfig],
        custom_model: str | None = None,
        custom_dimensions: int | None = None,
    ) -> Embeddings:
        """
        Dynamically decide and return the active Embeddings instance.
        """
        config_map = {cfg.provider.lower(): cfg for cfg in active_configs if cfg.is_active}

        # 1. Check if an explicit OpenAI config is present with embedding model
        if "openai" in config_map:
            cfg = config_map["openai"]
            if not cfg or not cfg.encrypted_api_key:
                raise ValueError("Active OpenAI configuration or encrypted API key is missing.")
            api_key = decrypt_api_key(cfg.encrypted_api_key)
            if not api_key:
                raise ValueError("Failed to decrypt API key for OpenAI provider.")
            embedding_model = custom_model or cfg.default_embedding_model or "text-embedding-3-small"
            dimensions = custom_dimensions or cfg.embedding_dimensions or 1536
            if not embedding_model:
                raise ValueError("Embedding model must be specified for OpenAI provider.")
            if not dimensions or dimensions <= 0:
                raise ValueError("Embedding dimensions must be a positive integer for OpenAI provider.")
            return OpenAIProvider(api_key=api_key, base_url=cfg.base_url).get_embeddings_model(
                model_name=embedding_model,
                dimensions=dimensions,
            )

        # 2. Check Gemini config
        elif "gemini" in config_map or "google" in config_map:
            cfg = config_map.get("gemini") or config_map.get("google")
            if not cfg or not cfg.encrypted_api_key:
                raise ValueError("Active Gemini configuration or encrypted API key is missing.")
            api_key = decrypt_api_key(cfg.encrypted_api_key)
            if not api_key:
                raise ValueError("Failed to decrypt API key for Gemini provider.")
            embedding_model = custom_model or cfg.default_embedding_model or "gemini-embedding-001"
            dimensions = custom_dimensions or cfg.embedding_dimensions or 1536
            if not embedding_model:
                raise ValueError("Embedding model must be specified for Gemini provider.")
            return GeminiProvider(api_key=api_key).get_embeddings_model(
                model_name=embedding_model,
                dimensions=dimensions,
            )

        # 3. Check Anthropic config (falls back to OpenAI embeddings model)
        elif "anthropic" in config_map:
            cfg = config_map["anthropic"]
            if not cfg or not cfg.encrypted_api_key:
                raise ValueError("Active Anthropic configuration or encrypted API key is missing.")
            api_key = decrypt_api_key(cfg.encrypted_api_key)
            if not api_key:
                raise ValueError("Failed to decrypt API key for Anthropic provider.")
            embedding_model = custom_model or cfg.default_embedding_model or "text-embedding-3-small"
            dimensions = custom_dimensions or cfg.embedding_dimensions or 1536
            if not embedding_model:
                raise ValueError("Embedding model must be specified for Anthropic embedding provider.")
            if not dimensions or dimensions <= 0:
                raise ValueError("Embedding dimensions must be a positive integer.")
            return AnthropicProvider(api_key=api_key, base_url=cfg.base_url).get_embeddings_model(
                model_name=embedding_model,
                dimensions=dimensions,
            )

        raise RuntimeError(
            "No active Embedding provider configured in the database. "
            "Please configure your LLM Provider (OpenAI, Anthropic, or Gemini) in the Settings page."
        )
