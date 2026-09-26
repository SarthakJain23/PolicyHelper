from app.core.config import settings
from app.services.llm.base import LLMProviderService
from app.services.llm.openai import OpenAIProvider
from app.services.llm.anthropic import AnthropicProvider
from app.services.llm.gemini import GeminiProvider

_llm_provider_instance: LLMProviderService | None = None


class LLMProviderFactory:
    """Factory to return configured LLM and Embeddings provider."""

    @staticmethod
    def get_provider() -> LLMProviderService:
        global _llm_provider_instance
        if _llm_provider_instance is None:
            provider_name = settings.LLM_PROVIDER.lower()
            if provider_name == "anthropic":
                _llm_provider_instance = AnthropicProvider()
            elif provider_name in ["gemini", "google"]:
                _llm_provider_instance = GeminiProvider()
            else:
                _llm_provider_instance = OpenAIProvider()
        return _llm_provider_instance


def get_llm_provider() -> LLMProviderService:
    """Convenience helper to get the active LLM provider instance."""
    return LLMProviderFactory.get_provider()
