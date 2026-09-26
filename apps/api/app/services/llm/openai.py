from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from app.core.config import settings
from app.services.llm.base import LLMProviderService


class OpenAIProvider(LLMProviderService):
    """OpenAI LLM and Embedding Provider Implementation."""

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.chat_model = settings.OPENAI_CHAT_MODEL
        self.fast_model = settings.OPENAI_FAST_MODEL
        self.embedding_model = settings.OPENAI_EMBEDDING_MODEL
        self.dimensions = settings.OPENAI_EMBEDDING_DIMENSIONS

    def get_chat_model(self, temperature: float = 0.0, streaming: bool = True) -> BaseChatModel:
        return ChatOpenAI(
            model=self.chat_model,
            temperature=temperature,
            streaming=streaming,
            api_key=self.api_key,
        )

    def get_fast_model(self, temperature: float = 0.0) -> BaseChatModel:
        return ChatOpenAI(
            model=self.fast_model,
            temperature=temperature,
            streaming=False,
            api_key=self.api_key,
        )

    def get_embeddings_model(self) -> Embeddings:
        return OpenAIEmbeddings(
            model=self.embedding_model,
            dimensions=self.dimensions,
            api_key=self.api_key,
        )
