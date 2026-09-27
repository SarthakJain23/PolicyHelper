import uuid
from typing import TypedDict, Literal
from langchain_core.messages import BaseMessage


class GraphState(TypedDict):
    """
    State container for the PolicyHelper LangGraph chat workflow.
    """
    # Context & identifiers
    session_id: uuid.UUID
    user_id: uuid.UUID
    user_roles: list[str]
    user_department_id: uuid.UUID | None
    model_name: str | None
    provider_name: str | None

    # Context window & Token management
    messages: list[BaseMessage]
    conversation_summary: str | None
    raw_query: str
    rewritten_query: str

    # Guardrails & Routing
    guardrail_status: Literal["passed", "blocked_safety", "blocked_domain"]
    guardrail_reason: str | None
    intent: Literal["rag", "direct_chat", "guardrail_rejection"]

    # RAG Artifacts
    retrieved_chunks: list[dict]
    relevant_chunks: list[dict]
    citations: list[dict]

    # Generation & Diagnostics
    generation: str
    is_fallback: bool
