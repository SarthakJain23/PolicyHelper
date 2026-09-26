import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Any
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.document import Document, DocumentStatus
from app.models.chunk import DocumentChunk
from app.models.organization import OrganizationLLMConfig
from app.services.llm.factory import LLMProviderFactory

logger = logging.getLogger(__name__)


class ReindexService:
    """
    Singleton Service to orchestrate background document re-embedding and vector re-indexing
    when the active embedding model or dimensions are updated.
    """

    _instance: "ReindexService | None" = None
    _tasks: dict[str, dict[str, Any]] = {}

    def __new__(cls) -> "ReindexService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tasks = {}
        return cls._instance

    @classmethod
    def get_instance(cls) -> "ReindexService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_task_status(self, task_id: str) -> dict[str, Any] | None:
        """Get the current progress status of a reindexing task."""
        return self._tasks.get(task_id)

    async def start_reindexing(
        self,
        org_id: uuid.UUID,
        new_embedding_model: str,
        dimensions: int = 1536,
    ) -> str:
        """Initiate asynchronous background re-indexing of all document chunks."""
        task_id = str(uuid.uuid4())
        self._tasks[task_id] = {
            "task_id": task_id,
            "organization_id": str(org_id),
            "status": "IN_PROGRESS",
            "new_embedding_model": new_embedding_model,
            "total_chunks": 0,
            "completed_chunks": 0,
            "progress_percentage": 0.0,
            "error": None,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": None,
        }

        # Spawn background execution
        asyncio.create_task(
            self._execute_reindexing(task_id, org_id, new_embedding_model, dimensions)
        )
        return task_id

    async def _execute_reindexing(
        self,
        task_id: str,
        org_id: uuid.UUID,
        new_embedding_model: str,
        dimensions: int,
    ) -> None:
        """Background execution loop: re-embed all chunks in batches with backoff."""
        logger.info(f"Starting reindexing task {task_id} for org {org_id} using {new_embedding_model}")

        try:
            async with AsyncSessionLocal() as session:
                # 1. Fetch total chunk count
                count_stmt = select(func.count(DocumentChunk.id))
                total_chunks = (await session.execute(count_stmt)).scalar() or 0
                self._tasks[task_id]["total_chunks"] = total_chunks

                if total_chunks == 0:
                    self._tasks[task_id]["status"] = "COMPLETED"
                    self._tasks[task_id]["progress_percentage"] = 100.0
                    self._tasks[task_id]["completed_at"] = datetime.now(timezone.utc).isoformat()
                    return

                # 2. Get the new Embeddings model
                embeddings_model = await LLMProviderFactory.get_embeddings(
                    db=session,
                    custom_model=new_embedding_model,
                    custom_dimensions=dimensions,
                )

                # 3. Process in batches of 50 chunks
                batch_size = 50
                offset = 0
                completed = 0

                while offset < total_chunks:
                    chunk_stmt = (
                        select(DocumentChunk)
                        .order_by(DocumentChunk.created_at)
                        .offset(offset)
                        .limit(batch_size)
                    )
                    chunks = (await session.execute(chunk_stmt)).scalars().all()
                    if not chunks:
                        break

                    texts = [c.content for c in chunks]
                    try:
                        new_vectors = await embeddings_model.aembed_documents(texts)
                        for idx, chunk in enumerate(chunks):
                            chunk.embedding = new_vectors[idx]
                            chunk.embedding_model = new_embedding_model
                        
                        await session.commit()
                        completed += len(chunks)
                        offset += batch_size

                        # Update progress
                        pct = round((completed / total_chunks) * 100, 2)
                        self._tasks[task_id]["completed_chunks"] = completed
                        self._tasks[task_id]["progress_percentage"] = pct
                        logger.info(f"Reindex Task {task_id}: {completed}/{total_chunks} chunks ({pct}%)")

                    except Exception as batch_err:
                        logger.error(f"Error re-embedding batch at offset {offset}: {batch_err}")
                        await asyncio.sleep(2)
                        # Retry once
                        new_vectors = await embeddings_model.aembed_documents(texts)
                        for idx, chunk in enumerate(chunks):
                            chunk.embedding = new_vectors[idx]
                            chunk.embedding_model = new_embedding_model
                        await session.commit()
                        completed += len(chunks)
                        offset += batch_size

                self._tasks[task_id]["status"] = "COMPLETED"
                self._tasks[task_id]["progress_percentage"] = 100.0
                self._tasks[task_id]["completed_at"] = datetime.now(timezone.utc).isoformat()
                logger.info(f"Reindexing task {task_id} completed successfully.")

        except Exception as e:
            logger.error(f"Reindexing task {task_id} failed: {e}", exc_info=True)
            self._tasks[task_id]["status"] = "FAILED"
            self._tasks[task_id]["error"] = str(e)
            self._tasks[task_id]["completed_at"] = datetime.now(timezone.utc).isoformat()
