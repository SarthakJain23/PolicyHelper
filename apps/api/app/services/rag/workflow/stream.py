import json
import logging
import uuid
from typing import AsyncGenerator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

from app.core.security import extract_user_roles
from app.models.user import User
from app.models.chat import ChatSession, ChatMessage, MessageCitation, MessageSender
from app.services.chat.title_service import generate_session_title_async
from app.services.llm.utils import extract_text_content
from app.services.rag.workflow.state import GraphState
from app.services.rag.workflow.builder import build_chat_graph

logger = logging.getLogger(__name__)


class ChatStreamService:
    """
    Singleton service that orchestrates LangGraph multi-agent execution
    and streams Server-Sent Events (SSE) to clients.
    """
    _instance: "ChatStreamService | None" = None

    def __new__(cls) -> "ChatStreamService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return
        self._graph = None
        self._initialized = True

    def get_graph(self):
        """Lazy-load and cache the compiled LangGraph workflow instance."""
        if self._graph is None:
            self._graph = build_chat_graph()
        return self._graph

    @staticmethod
    def format_sse_event(event: str, data: dict) -> str:
        """Format an event and payload conforming to the SSE text/event-stream spec."""
        return f"data: {json.dumps({'event': event, 'data': data})}\n\n"

    async def fetch_session(
        self,
        session_id: uuid.UUID,
        model_name: str | None,
        db: AsyncSession,
    ) -> ChatSession | None:
        """Retrieve chat session and sync user-selected model if provided."""
        session = await db.get(ChatSession, session_id)
        if session and model_name:
            session.selected_model = model_name
        return session

    async def fetch_history_messages(
        self,
        session_id: uuid.UUID,
        db: AsyncSession,
        limit: int = 10,
    ) -> list[BaseMessage]:
        """Fetch recent conversation turn history from the database."""
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
        )
        res = await db.execute(stmt)
        prior_db_messages = list(reversed(res.scalars().all()))

        history_messages: list[BaseMessage] = []
        for m in prior_db_messages:
            if m.sender == MessageSender.USER.value:
                history_messages.append(HumanMessage(content=m.content))
            elif m.sender == MessageSender.ASSISTANT.value:
                history_messages.append(AIMessage(content=m.content))
        return history_messages

    async def persist_user_message(
        self,
        session: ChatSession,
        content: str,
        db: AsyncSession,
    ) -> ChatMessage:
        """Persist the incoming user message to PostgreSQL."""
        user_msg = ChatMessage(
            session_id=session.id,
            sender=MessageSender.USER.value,
            content=content,
        )
        db.add(user_msg)
        session.message_count += 1
        await db.commit()
        await db.refresh(user_msg)
        return user_msg

    def build_initial_state(
        self,
        session: ChatSession,
        current_user: User,
        user_message_content: str,
        history_messages: list[BaseMessage],
        model_name: str | None,
        provider_name: str | None,
    ) -> GraphState:
        """Construct the initial typed state for the LangGraph workflow."""
        user_roles = extract_user_roles(current_user)
        return {
            "session_id": session.id,
            "user_id": current_user.id,
            "user_roles": user_roles,
            "user_department_id": current_user.department_id,
            "model_name": model_name or session.selected_model,
            "provider_name": provider_name,
            "messages": history_messages,
            "conversation_summary": None,
            "raw_query": user_message_content,
            "rewritten_query": user_message_content,
            "guardrail_status": "passed",
            "guardrail_reason": None,
            "intent": "rag",
            "retrieved_chunks": [],
            "relevant_chunks": [],
            "citations": [],
            "generation": "",
            "is_fallback": False,
        }

    async def persist_assistant_message(
        self,
        session: ChatSession,
        response_text: str,
        citations: list[dict],
        last_state: dict | None,
        db: AsyncSession,
    ) -> ChatMessage:
        """Persist assistant completion message and associated citations."""
        assistant_msg = ChatMessage(
            session_id=session.id,
            sender=MessageSender.ASSISTANT.value,
            content=response_text,
            metadata_={
                "retrieved_chunk_count": len(citations),
                "intent": last_state.get("intent") if last_state else "rag",
                "guardrail_status": last_state.get("guardrail_status") if last_state else "passed",
            },
        )
        db.add(assistant_msg)
        session.message_count += 1
        await db.flush()

        for c_data in citations:
            citation_entry = MessageCitation(
                message_id=assistant_msg.id,
                chunk_id=uuid.UUID(c_data["chunk_id"]) if c_data.get("chunk_id") else None,
                document_id=uuid.UUID(c_data["document_id"]),
                document_title=c_data["document_title"],
                page_number=c_data.get("page_number"),
                snippet=c_data.get("snippet", ""),
                relevance_score=c_data.get("relevance_score"),
            )
            db.add(citation_entry)

        await db.commit()
        return assistant_msg

    async def check_and_trigger_auto_title(
        self,
        session: ChatSession,
        user_message_content: str,
    ) -> str | None:
        """Trigger background LLM agent to summarize and auto-title conversation after first turn."""
        if session.message_count >= 2 and not session.is_title_auto_generated:
            return await generate_session_title_async(session.id, user_message_content)
        return None

    async def stream_chat(
        self,
        session_id: uuid.UUID,
        user_message_content: str,
        current_user: User,
        db: AsyncSession,
        model_name: str | None = None,
        provider_name: str | None = None,
    ) -> AsyncGenerator[str, None]:
        """
        Executes LangGraph via astream_events v2 and yields Server-Sent Events (SSE).
        """
        # 1. Fetch Session
        session = await self.fetch_session(session_id, model_name, db)
        if not session:
            yield self.format_sse_event("error", {"message": "Session not found"})
            return

        # 2. Fetch History & Persist User Message
        history_messages = await self.fetch_history_messages(session.id, db)
        await self.persist_user_message(session, user_message_content, db)

        # 3. Prepare Initial Graph State
        initial_state = self.build_initial_state(
            session=session,
            current_user=current_user,
            user_message_content=user_message_content,
            history_messages=history_messages,
            model_name=model_name,
            provider_name=provider_name,
        )

        graph = self.get_graph()
        config = {"configurable": {"db": db}}

        full_response_text = ""
        accumulated_citations: list[dict] = []
        last_state = None

        try:
            # 4. Stream Graph Execution Events via astream_events v2
            async for event in graph.astream_events(initial_state, config=config, version="v2"):
                kind = event.get("event")

                # Custom Citation Events from retriever_node
                if kind == "on_custom_event" and event.get("name") == "citation":
                    citation_data = event.get("data", {})
                    accumulated_citations.append(citation_data)
                    yield self.format_sse_event("citation", citation_data)

                # Real-time LLM Token Chunks from generator_node or direct_chat_node
                elif kind == "on_chat_model_stream":
                    # Ensure tokens are only captured from actual answer-generating nodes
                    node_name = event.get("metadata", {}).get("langgraph_node")
                    if node_name and node_name not in ("generator", "direct_chat"):
                        continue

                    chunk = event.get("data", {}).get("chunk")
                    if chunk:
                        token_text = extract_text_content(getattr(chunk, "content", chunk))
                        if token_text:
                            full_response_text += token_text
                            yield self.format_sse_event("token", {"content": token_text})

                # Capture end state from graph
                elif kind == "on_chain_end" and event.get("name") == "LangGraph":
                    output = event.get("data", {}).get("output")
                    if isinstance(output, dict):
                        last_state = output

            # Handle static fallback or guardrail text if no tokens were streamed
            if not full_response_text and last_state and last_state.get("generation"):
                full_response_text = extract_text_content(last_state.get("generation", ""))
                if full_response_text:
                    yield self.format_sse_event("token", {"content": full_response_text})

            if not full_response_text:
                full_response_text = "I apologize, but I could not process your request at this time."
                yield self.format_sse_event("token", {"content": full_response_text})

            # 5. Persist Assistant Message and Citations to DB
            assistant_msg = await self.persist_assistant_message(
                session=session,
                response_text=full_response_text,
                citations=accumulated_citations,
                last_state=last_state,
                db=db,
            )

            # 6. Auto-Title Trigger
            new_title = await self.check_and_trigger_auto_title(session, user_message_content)
            if new_title:
                yield self.format_sse_event(
                    "session_updated",
                    {"session_id": str(session.id), "title": new_title},
                )

            # 7. Emit Done Event
            yield self.format_sse_event("done", {"message_id": str(assistant_msg.id)})

        except Exception as e:
            logger.error(f"Error during LangGraph streaming: {e}", exc_info=True)
            yield self.format_sse_event("error", {"message": f"Streaming error: {str(e)}"})


def get_chat_stream_service() -> ChatStreamService:
    """Returns the singleton instance of ChatStreamService."""
    return ChatStreamService()


async def stream_langgraph_chat(
    session_id: uuid.UUID,
    user_message_content: str,
    current_user: User,
    db: AsyncSession,
    model_name: str | None = None,
    provider_name: str | None = None,
) -> AsyncGenerator[str, None]:
    """
    Convenience function routing to the singleton ChatStreamService instance.
    """
    service = get_chat_stream_service()
    async for line in service.stream_chat(
        session_id=session_id,
        user_message_content=user_message_content,
        current_user=current_user,
        db=db,
        model_name=model_name,
        provider_name=provider_name,
    ):
        yield line
