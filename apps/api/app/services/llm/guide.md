# LLM Provider Strategy Guide (`apps/api/app/services/llm/`)

Implementation of the **LLM Provider Strategy Pattern** supporting OpenAI, Anthropic Claude, and Google Gemini.

---

## File Index

| File                           | Description                                                                                         |
| :----------------------------- | :-------------------------------------------------------------------------------------------------- |
| [`base.py`](base.py)           | Abstract base class `LLMProviderService` defining chat models, fast models, and embeddings methods. |
| [`openai.py`](openai.py)       | `OpenAIProvider` integrating `ChatOpenAI` and `OpenAIEmbeddings`.                                   |
| [`anthropic.py`](anthropic.py) | `AnthropicProvider` integrating `ChatAnthropic` (Claude 3.5 Sonnet).                                |
| [`gemini.py`](gemini.py)       | `GeminiProvider` integrating `ChatGoogleGenerativeAI` and `GoogleGenerativeAIEmbeddings`.           |
| [`factory.py`](factory.py)     | `LLMProviderFactory` resolving provider via `LLM_PROVIDER` in `.env`.                               |
