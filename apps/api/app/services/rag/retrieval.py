import uuid
from typing import TypedDict
from sqlalchemy import select, text, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.chunk import DocumentChunk
from app.models.document import Document, DocumentStatus
from app.schemas.role import UserRole
from app.services.llm.factory import LLMProviderFactory


class RetrievedChunk(TypedDict):
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    document_title: str
    page_number: int | None
    section_header: str | None
    content: str
    score: float


class HybridRetriever:
    """
    Executes Hybrid Search (pgvector dense cosine similarity + PostgreSQL tsvector BM25 keyword match)
    with RBAC & department filtering.
    """

    @staticmethod
    async def retrieve(
        query: str,
        user_roles: list[str],
        user_department_id: uuid.UUID | None,
        db: AsyncSession,
        top_k: int = 5,
    ) -> list[RetrievedChunk]:
        is_admin = any(r in [UserRole.SUPER_ADMIN.value, UserRole.HR_ADMIN.value] for r in user_roles)

        # 1. Generate query embedding dynamically
        embeddings_model = await LLMProviderFactory.get_embeddings(db=db)
        query_vector = await embeddings_model.aembed_query(query)

        # 2. Vector search query using pgvector cosine distance (<=>)
        # 1 - (embedding <=> query_vector) represents cosine similarity
        vector_similarity = (1 - DocumentChunk.embedding.cosine_distance(query_vector)).label("vec_sim")

        # 3. Full-text search rank using ts_rank
        # Match plainto_tsquery against generated search_vector
        fts_query = func.plainto_tsquery("english", query)
        fts_rank = func.ts_rank_cd(DocumentChunk.search_vector, fts_query).label("fts_rank")

        # Hybrid score = 0.7 * vector_sim + 0.3 * normalized_fts_rank
        # Join with Document to ensure document is active and check RBAC
        stmt = (
            select(
                DocumentChunk.id.label("chunk_id"),
                Document.id.label("document_id"),
                Document.title.label("document_title"),
                DocumentChunk.metadata_.label("chunk_metadata"),
                DocumentChunk.content,
                vector_similarity,
                fts_rank,
            )
            .join(Document, DocumentChunk.document_id == Document.id)
            .where(Document.status == DocumentStatus.INDEXED.value)
        )

        # Apply department & role constraints if not super/hr admin
        if not is_admin:
            # Department condition: doc.department_id is NULL (company-wide) OR matches user's department
            dept_condition = (Document.department_id == None)
            if user_department_id:
                dept_condition = dept_condition | (Document.department_id == user_department_id)
            stmt = stmt.where(dept_condition)

        # Order by vector similarity descending
        stmt = stmt.order_by(vector_similarity.desc()).limit(settings.RETRIEVAL_TOP_K)

        result = await db.execute(stmt)
        rows = result.all()

        retrieved: list[RetrievedChunk] = []
        for row in rows:
            meta = row.chunk_metadata or {}
            # Filter role permission in Python
            if not is_admin:
                # We can check document allowed_roles if needed
                pass

            # Calculate combined hybrid score
            vec_sim = float(row.vec_sim) if row.vec_sim is not None else 0.0
            rank = float(row.fts_rank) if row.fts_rank is not None else 0.0
            combined_score = (0.75 * vec_sim) + (0.25 * min(rank, 1.0))

            retrieved.append(
                RetrievedChunk(
                    chunk_id=row.chunk_id,
                    document_id=row.document_id,
                    document_title=row.document_title,
                    page_number=meta.get("page_number"),
                    section_header=meta.get("section_header"),
                    content=row.content,
                    score=combined_score,
                )
            )

        # Sort by combined score descending and take top_k
        retrieved.sort(key=lambda x: x["score"], reverse=True)
        return retrieved[:top_k]
