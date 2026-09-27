import logging
from langchain_core.callbacks.manager import adispatch_custom_event
from langchain_core.runnables import RunnableConfig
from app.services.rag.retrieval import HybridRetriever
from app.services.rag.workflow.state import GraphState

logger = logging.getLogger(__name__)


async def retriever_node(state: GraphState, config: RunnableConfig) -> dict:
    """
    Executes hybrid search with RBAC role and department constraints.
    Dispatches SSE 'citation' custom events in real time.
    """
    search_query = state.get("rewritten_query") or state.get("raw_query", "")
    user_roles = state.get("user_roles", [])
    user_dept_id = state.get("user_department_id")
    db = config.get("configurable", {}).get("db")

    if not db or not search_query.strip():
        return {"retrieved_chunks": [], "citations": []}

    try:
        retrieved_chunks = await HybridRetriever.retrieve(
            query=search_query,
            user_roles=user_roles,
            user_department_id=user_dept_id,
            db=db,
            top_k=4,
        )

        citations_list = []
        for chunk in retrieved_chunks:
            citation_item = {
                "chunk_id": str(chunk["chunk_id"]),
                "document_id": str(chunk["document_id"]),
                "document_title": chunk["document_title"],
                "page_number": chunk["page_number"],
                "snippet": chunk["content"][:300],
                "relevance_score": round(chunk["score"], 3),
            }
            citations_list.append(citation_item)
            # Dispatch event to the streaming receiver
            await adispatch_custom_event("citation", citation_item, config=config)

        logger.info(f"Retrieved {len(retrieved_chunks)} policy chunks for query '{search_query}'")
        return {
            "retrieved_chunks": retrieved_chunks,
            "citations": citations_list,
        }

    except Exception as e:
        logger.error(f"Error during retrieval: {e}", exc_info=True)
        return {"retrieved_chunks": [], "citations": []}
