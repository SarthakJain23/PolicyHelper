import json
import logging
from typing import AsyncGenerator
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from app.models.user import User
from app.models.chat import ChatSession, ChatMessage, MessageCitation, MessageSender
from app.services.llm.factory import get_llm_provider
from app.services.rag.retrieval import HybridRetriever, RetrievedChunk
from app.services.chat.title_service import generate_session_title_async

logger = logging.getLogger(__name__)

RAG_SYSTEM_PROMPT = """You are PolicyHelper, the dedicated internal policy assistant for company employees.

Your job is to provide accurate, helpful, and concise answers based STRICTLY on the provided company policy documents below.

GUIDELINES:
1. Grounding: Rely exclusively on the provided context sections. Do not extrapolate, assume, or invent company rules.
2. Citations: When referencing a rule, cite the document title and page number (e.g. "[Doc: Leave Policy 2026, Page: 4]").
3. Missing Information: If the provided documents do not contain the answer or if the question is unrelated to company policy, clearly state:
   "I could not find information regarding this in the company's uploaded policy documents. Please consult HR or your department lead directly."
4. Tone: Professional, direct, polite, and neutral. Use markdown bullet points and bold highlights for readability.

---
POLICY CONTEXT:
{context}
"""


async def stream_rag_chat(
    session_id: uuid.UUID,
    user_message_content: str,
    current_user: User,
    db: AsyncSession,
) -> AsyncGenerator[str, None]:
    """
    Executes LangChain / LangGraph RAG workflow and yields Server-Sent Events (SSE).
    Format:
      data: {"event": "citation", "data": {...}}\n\n
      data: {"event": "token", "data": {"content": "..."}}\n\n
      data: {"event": "session_updated", "data": {"title": "..."}}\n\n
      data: {"event": "done", "data": {"message_id": "..."}}\n\n
    """
    user_roles = [r.name for r in current_user.roles]

    # 1. Fetch Session and Recent Chat History
    session = await db.get(ChatSession, session_id)
    if not session:
        yield f"data: {json.dumps({'event': 'error', 'data': {'message': 'Session not found'}})}\n\n"
        return

    # 2. Persist User Message to DB
    user_msg = ChatMessage(
        session_id=session.id,
        sender=MessageSender.USER.value,
        content=user_message_content,
    )
    db.add(user_msg)
    session.message_count += 1
    await db.commit()
    await db.refresh(user_msg)

    try:
        # 3. Hybrid Retrieval with RBAC filtering
        retrieved_chunks = await HybridRetriever.retrieve(
            query=user_message_content,
            user_roles=user_roles,
            user_department_id=current_user.department_id,
            db=db,
            top_k=4,
        )

        # 4. Yield Citations Event to Client
        citations_data = []
        for chunk in retrieved_chunks:
            citation_item = {
                "chunk_id": str(chunk["chunk_id"]),
                "document_id": str(chunk["document_id"]),
                "document_title": chunk["document_title"],
                "page_number": chunk["page_number"],
                "snippet": chunk["content"][:300],
                "relevance_score": round(chunk["score"], 3),
            }
            citations_data.append(citation_item)
            yield f"data: {json.dumps({'event': 'citation', 'data': citation_item})}\n\n"

        # 5. Build Context String
        if retrieved_chunks:
            context_blocks = []
            for i, chunk in enumerate(retrieved_chunks, 1):
                page_info = f", Page {chunk['page_number']}" if chunk['page_number'] else ""
                context_blocks.append(
                    f"--- Source [{i}]: {chunk['document_title']}{page_info} ---\n{chunk['content']}\n"
                )
            context_str = "\n".join(context_blocks)
        else:
            context_str = "No matching policy documents found in the database."

        # 6. Stream LLM Response
        llm_provider = get_llm_provider()
        chat_model = llm_provider.get_chat_model(temperature=0.1, streaming=True)

        system_instruction = RAG_SYSTEM_PROMPT.format(context=context_str)
        messages = [
            SystemMessage(content=system_instruction),
            HumanMessage(content=user_message_content),
        ]

        full_response_text = ""
        async for chunk in chat_model.astream(messages):
            token_text = chunk.content if isinstance(chunk.content, str) else str(chunk.content)
            if token_text:
                full_response_text += token_text
                yield f"data: {json.dumps({'event': 'token', 'data': {'content': token_text}})}\n\n"

        # 7. Persist Assistant Message and Citations to DB
        assistant_msg = ChatMessage(
            session_id=session.id,
            sender=MessageSender.ASSISTANT.value,
            content=full_response_text,
            metadata_={"retrieved_chunk_count": len(retrieved_chunks)},
        )
        db.add(assistant_msg)
        session.message_count += 1
        await db.flush()

        for c_data in citations_data:
            citation_entry = MessageCitation(
                message_id=assistant_msg.id,
                chunk_id=uuid.UUID(c_data["chunk_id"]) if c_data["chunk_id"] else None,
                document_id=uuid.UUID(c_data["document_id"]),
                document_title=c_data["document_title"],
                page_number=c_data["page_number"],
                snippet=c_data["snippet"],
                relevance_score=c_data["relevance_score"],
            )
            db.add(citation_entry)

        await db.commit()

        # 8. Check for Auto-Titling Trigger (after first turn / message_count >= 2)
        if session.message_count >= 2 and not session.is_title_auto_generated:
            new_title = await generate_session_title_async(session.id, user_message_content)
            if new_title:
                yield f"data: {json.dumps({'event': 'session_updated', 'data': {'session_id': str(session.id), 'title': new_title}})}\n\n"

        # 9. Yield Done Event
        yield f"data: {json.dumps({'event': 'done', 'data': {'message_id': str(assistant_msg.id)}})}\n\n"

    except Exception as e:
        logger.error(f"Error during RAG streaming: {e}", exc_info=True)
        yield f"data: {json.dumps({'event': 'error', 'data': {'message': f'Streaming error: {str(e)}'}})}\n\n"
