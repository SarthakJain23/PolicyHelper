import logging
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.core.database import AsyncSessionLocal
from app.models.document import Document, DocumentStatus
from app.models.chunk import DocumentChunk
from app.services.storage.factory import get_storage
from app.services.llm.factory import LLMProviderFactory
from app.services.ingestion.parser import DocumentParser
from app.services.ingestion.chunker import PolicyChunker

logger = logging.getLogger(__name__)


async def process_document_ingestion(document_id: uuid.UUID) -> None:
    """
    Background job:
    1. Downloads raw document bytes from configured storage
    2. Parses document into structured sections (preserving page numbers)
    3. Chunks with breadcrumbs using PolicyChunker
    4. Generates batch vector embeddings via selected LLMProvider
    5. Stores chunks in PostgreSQL (with pgvector embedding + tsvector search_vector)
    6. Updates Document status to INDEXED or FAILED
    """
    async with AsyncSessionLocal() as session:
        doc = await session.get(Document, document_id)
        if not doc:
            logger.error(f"Document {document_id} not found for ingestion")
            return

        try:
            doc.status = DocumentStatus.PROCESSING.value
            await session.commit()

            # 1. Download file bytes from storage
            storage = get_storage()
            file_bytes = await storage.download_file(doc.file_path)

            # 2. Parse document text
            sections = DocumentParser.parse(file_bytes, doc.file_type)
            if not sections:
                raise ValueError("No extractable text found in document")

            # 3. Chunk text with breadcrumb context
            chunker = PolicyChunker()
            chunk_results = chunker.chunk_document(
                document_title=doc.title,
                category=doc.category,
                sections=sections,
            )

            if not chunk_results:
                raise ValueError("Document yielded 0 chunks after splitting")

            # 4. Generate batch embeddings using active organization embedding model
            embeddings_model = await LLMProviderFactory.get_embeddings(db=session)
            chunk_texts = [c["content"] for c in chunk_results]

            # Embedding API call
            vectors = await embeddings_model.aembed_documents(chunk_texts)

            # 5. Clean any existing chunks for this document
            await session.execute(
                delete(DocumentChunk).where(DocumentChunk.document_id == document_id)
            )

            # 6. Insert new chunks
            for i, chunk_data in enumerate(chunk_results):
                vector = vectors[i] if i < len(vectors) else None
                new_chunk = DocumentChunk(
                    document_id=doc.id,
                    chunk_index=chunk_data["chunk_index"],
                    content=chunk_data["content"],
                    metadata_=chunk_data["metadata"],
                    embedding=vector,
                )
                session.add(new_chunk)

            # 7. Mark as INDEXED
            doc.status = DocumentStatus.INDEXED.value
            doc.error_message = None
            await session.commit()
            logger.info(
                f"Successfully ingested and indexed document {doc.title} ({len(chunk_results)} chunks)"
            )

        except Exception as e:
            logger.error(f"Error ingesting document {document_id}: {e}", exc_info=True)
            doc.status = DocumentStatus.FAILED.value
            doc.error_message = str(e)
            await session.commit()
