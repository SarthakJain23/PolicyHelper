from abc import ABC, abstractmethod
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings


class LLMProviderService(ABC):
    """Abstract Base Class for LLM and Embedding Provider strategies."""

    @abstractmethod
    def get_chat_model(
        self,
        model_name: str | None = None,
        temperature: float = 0.0,
        streaming: bool = True,
    ) -> BaseChatModel:
        """Return the primary Chat Model for conversational RAG generation."""
        pass

    @abstractmethod
    def get_fast_model(
        self,
        model_name: str | None = None,
        temperature: float = 0.0,
    ) -> BaseChatModel:
        """Return a lightweight, fast model for query rewriting and auto-titling."""
        pass

    @abstractmethod
    def get_embeddings_model(
        self,
        model_name: str | None = None,
        dimensions: int | None = None,
    ) -> Embeddings:
        """Return the Embeddings model for document chunking and vector search."""
        pass

