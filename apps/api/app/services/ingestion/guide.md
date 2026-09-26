# Document Ingestion Guide (`apps/api/app/services/ingestion/`)

Document parsing, header-aware chunking, embedding generation, and vector database persistence.

---

## File Index

| File                         | Description                                                                                                                                               |
| :--------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`parser.py`](parser.py)     | `DocumentParser` extracting text from `.pdf`, `.docx`, `.md`, and `.txt` files with page numbering.                                                       |
| [`chunker.py`](chunker.py)   | `PolicyChunker` implementing **Hybrid Header-Aware + Recursive Splitting** with breadcrumb context injection.                                             |
| [`pipeline.py`](pipeline.py) | `process_document_ingestion` async worker executing download $\rightarrow$ parse $\rightarrow$ chunk $\rightarrow$ embed $\rightarrow$ pgvector indexing. |
