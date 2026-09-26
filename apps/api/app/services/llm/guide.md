# LLM Provider Strategy Guide (`apps/api/app/services/llm/`)

Implementation of the **LLM Provider Strategy Pattern** supporting OpenAI, Anthropic Claude, and Google Gemini.

---

## File Index

| File                                     | Description                                                                                          |
| :--------------------------------------- | :--------------------------------------------------------------------------------------------------- |
| [`base.py`](base.py)                     | Abstract base class `LLMProviderService` defining chat models, fast models, and embeddings methods.  |
| [`openai.py`](openai.py)                 | `OpenAIProvider` integrating `ChatOpenAI` and `OpenAIEmbeddings`.                                    |
| [`anthropic.py`](anthropic.py)           | `AnthropicProvider` integrating `ChatAnthropic` (Claude 3.5 Sonnet / Haiku).                         |
| [`gemini.py`](gemini.py)                 | `GeminiProvider` integrating `ChatGoogleGenerativeAI` and `GoogleGenerativeAIEmbeddings`.            |
| [`discovery.py`](discovery.py)           | `ModelDiscoveryService` singleton for querying live vendor APIs and caching available model choices. |
| [`decision_agent.py`](decision_agent.py) | `LLMDecisionAgent` LangChain agent for autonomous fast-model and embeddings selection.               |
| [`factory.py`](factory.py)               | `LLMProviderFactory` dynamically resolving providers and models from encrypted database records.     |
