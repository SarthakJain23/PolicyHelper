from langchain_anthropic import ChatAnthropic
from langchain_openai import OpenAIEmbeddings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from app.core.config import settings
from app.services.llm.base import LLMProviderService


class AnthropicProvider(LLMProviderService):
    """Anthropic Claude LLM Provider Implementation."""

    def __init__(self):
        self.api_key = settings.ANTHROPIC_API_KEY
        self.chat_model = settings.ANTHROPIC_CHAT_MODEL

    def get_chat_model(self, temperature: float = 0.0, streaming: bool = True) -> BaseChatModel:
        return ChatAnthropic(
            model_name=self.chat_model,
            temperature=temperature,
            streaming=streaming,
            api_key=self.api_key,
        )

    def get_fast_model(self, temperature: float = 0.0) -> BaseChatModel:
        return ChatAnthropic(
            model_name="claude-3-5-haiku-20241022",
            temperature=temperature,
            streaming=False,
            api_key=self.api_key,
        )

    def get_embeddings_model(self) -> Embeddings:
        # Anthropic does not have a native embeddings API, falls back to OpenAI or local embeddings
        return OpenAIEmbeddings(
            model=settings.OPENAI_EMBEDDING_MODEL,
            api_key=settings.OPENAI_API_KEY,
        )
