from langchain_anthropic import ChatAnthropic
from langchain_openai import OpenAIEmbeddings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from app.services.llm.base import LLMProviderService


class AnthropicProvider(LLMProviderService):
    """Anthropic Claude LLM Provider Implementation."""

    def __init__(
        self,
        api_key: str,
        chat_model: str = "claude-3-5-sonnet-20241022",
        fast_model: str = "claude-3-5-haiku-20241022",
        base_url: str | None = None,
    ):
        if not api_key:
            raise ValueError("api_key must be provided to instantiate AnthropicProvider")
        self.api_key = api_key
        self.chat_model = chat_model
        self.fast_model = fast_model
        self.base_url = base_url

    def get_chat_model(
        self,
        model_name: str | None = None,
        temperature: float = 0.0,
        streaming: bool = True,
    ) -> BaseChatModel:
        kwargs = {
            "model_name": model_name or self.chat_model,
            "temperature": temperature,
            "streaming": streaming,
            "api_key": self.api_key,
        }
        if self.base_url:
            kwargs["anthropic_api_url"] = self.base_url
        return ChatAnthropic(**kwargs)

    def get_fast_model(
        self,
        model_name: str | None = None,
        temperature: float = 0.0,
    ) -> BaseChatModel:
        kwargs = {
            "model_name": model_name or self.fast_model,
            "temperature": temperature,
            "streaming": False,
            "api_key": self.api_key,
        }
        if self.base_url:
            kwargs["anthropic_api_url"] = self.base_url
        return ChatAnthropic(**kwargs)

    def get_embeddings_model(
        self,
        model_name: str | None = None,
        dimensions: int | None = None,
    ) -> Embeddings:
        # Anthropic does not provide native embeddings API, falls back to OpenAI-compatible embeddings
        return OpenAIEmbeddings(
            model=model_name or "text-embedding-3-small",
            dimensions=dimensions or 1536,
        )

