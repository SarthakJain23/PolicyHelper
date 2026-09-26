# RAG Retrieval & Orchestration Guide (`apps/api/app/services/rag/`)

Hybrid retrieval, LangGraph/LangChain RAG pipeline, and Server-Sent Events token streaming engine.

---

## File Index

| File                           | Description                                                                                                                             |
| :----------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------- |
| [`retrieval.py`](retrieval.py) | `HybridRetriever` executing dense `pgvector` cosine similarity + sparse `tsvector` keyword search with RBAC filters.                    |
| [`graph.py`](graph.py)         | `stream_rag_chat` orchestrating query context, hybrid search, grounded prompt synthesis, SSE token streaming, and citation persistence. |
