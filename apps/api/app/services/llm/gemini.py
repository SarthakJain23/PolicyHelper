from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from app.services.llm.base import LLMProviderService


class GeminiProvider(LLMProviderService):
    """Google Gemini LLM and Embedding Provider Implementation."""

    def __init__(
        self,
        api_key: str,
        chat_model: str = "gemini-1.5-pro",
        fast_model: str = "gemini-1.5-flash",
        embedding_model: str = "models/text-embedding-004",
    ):
        if not api_key:
            raise ValueError("api_key must be provided to instantiate GeminiProvider")
        self.api_key = api_key
        self.chat_model = chat_model
        self.fast_model = fast_model
        self.embedding_model = embedding_model

    def get_chat_model(
        self,
        model_name: str | None = None,
        temperature: float = 0.0,
        streaming: bool = True,
    ) -> BaseChatModel:
        return ChatGoogleGenerativeAI(
            model=model_name or self.chat_model,
            temperature=temperature,
            streaming=streaming,
            google_api_key=self.api_key,
        )

    def get_fast_model(
        self,
        model_name: str | None = None,
        temperature: float = 0.0,
    ) -> BaseChatModel:
        return ChatGoogleGenerativeAI(
            model=model_name or self.fast_model,
            temperature=temperature,
            streaming=False,
            google_api_key=self.api_key,
        )

    def get_embeddings_model(
        self,
        model_name: str | None = None,
        dimensions: int | None = None,
    ) -> Embeddings:
        return GoogleGenerativeAIEmbeddings(
            model=model_name or self.embedding_model,
            google_api_key=self.api_key,
        )

