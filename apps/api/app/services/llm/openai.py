from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from app.services.llm.base import LLMProviderService


class OpenAIProvider(LLMProviderService):
    """OpenAI LLM and Embedding Provider Implementation."""

    def __init__(
        self,
        api_key: str,
        chat_model: str = "gpt-4o",
        fast_model: str = "gpt-4o-mini",
        embedding_model: str = "text-embedding-3-small",
        dimensions: int = 1536,
        base_url: str | None = None,
    ):
        if not api_key:
            raise ValueError("api_key must be provided to instantiate OpenAIProvider")
        self.api_key = api_key
        self.chat_model = chat_model
        self.fast_model = fast_model
        self.embedding_model = embedding_model
        self.dimensions = dimensions
        self.base_url = base_url

    def get_chat_model(
        self,
        model_name: str | None = None,
        temperature: float = 0.0,
        streaming: bool = True,
    ) -> BaseChatModel:
        kwargs = {
            "model": model_name or self.chat_model,
            "temperature": temperature,
            "streaming": streaming,
            "api_key": self.api_key,
        }
        if self.base_url:
            kwargs["base_url"] = self.base_url
        return ChatOpenAI(**kwargs)

    def get_fast_model(
        self,
        model_name: str | None = None,
        temperature: float = 0.0,
    ) -> BaseChatModel:
        kwargs = {
            "model": model_name or self.fast_model,
            "temperature": temperature,
            "streaming": False,
            "api_key": self.api_key,
        }
        if self.base_url:
            kwargs["base_url"] = self.base_url
        return ChatOpenAI(**kwargs)

    def get_embeddings_model(
        self,
        model_name: str | None = None,
        dimensions: int | None = None,
    ) -> Embeddings:
        kwargs = {
            "model": model_name or self.embedding_model,
            "dimensions": dimensions or self.dimensions,
            "api_key": self.api_key,
        }
        if self.base_url:
            kwargs["base_url"] = self.base_url
        return OpenAIEmbeddings(**kwargs)

