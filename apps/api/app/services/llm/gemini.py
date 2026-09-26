from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings
from app.core.config import settings
from app.services.llm.base import LLMProviderService


class GeminiProvider(LLMProviderService):
    """Google Gemini LLM and Embedding Provider Implementation."""

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY or settings.GOOGLE_API_KEY
        self.chat_model = settings.GEMINI_CHAT_MODEL
        self.fast_model = settings.GEMINI_FAST_MODEL
        self.embedding_model = settings.GEMINI_EMBEDDING_MODEL

    def get_chat_model(self, temperature: float = 0.0, streaming: bool = True) -> BaseChatModel:
        return ChatGoogleGenerativeAI(
            model=self.chat_model,
            temperature=temperature,
            streaming=streaming,
            google_api_key=self.api_key,
        )

    def get_fast_model(self, temperature: float = 0.0) -> BaseChatModel:
        return ChatGoogleGenerativeAI(
            model=self.fast_model,
            temperature=temperature,
            streaming=False,
            google_api_key=self.api_key,
        )

    def get_embeddings_model(self) -> Embeddings:
        return GoogleGenerativeAIEmbeddings(
            model=self.embedding_model,
            google_api_key=self.api_key,
        )
