# Services Guide (`apps/api/app/services/`)

Contains core business logic, strategy patterns, document ingestion, and LangGraph RAG workflows.

---

## Subdirectories

| Subdirectory               | Description                                                                              | Link                                            |
| :------------------------- | :--------------------------------------------------------------------------------------- | :---------------------------------------------- |
| [`storage/`](storage/)     | Storage Strategy Pattern (`LocalStorageService`, `S3StorageService`).                    | [View `storage/guide.md`](storage/guide.md)     |
| [`llm/`](llm/)             | LLM Provider Strategy Pattern (`OpenAIProvider`, `AnthropicProvider`, `GeminiProvider`). | [View `llm/guide.md`](llm/guide.md)             |
| [`ingestion/`](ingestion/) | Document parsing, header-aware chunking, and embedding pipeline.                         | [View `ingestion/guide.md`](ingestion/guide.md) |
| [`rag/`](rag/)             | Hybrid retrieval and LangGraph SSE token streaming engine.                               | [View `rag/guide.md`](rag/guide.md)             |
| [`chat/`](chat/)           | Chat utilities and automated session title generation.                                   | [View `chat/guide.md`](chat/guide.md)           |
