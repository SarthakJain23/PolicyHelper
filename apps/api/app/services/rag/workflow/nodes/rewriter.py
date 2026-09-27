import logging
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from app.services.llm.factory import LLMProviderFactory
from app.services.rag.workflow.state import GraphState

logger = logging.getLogger(__name__)

REWRITER_PROMPT = """You are a search query reformulation expert for a corporate policy retrieval system.

Given the conversation summary, recent chat history, and the user's latest question, rewrite the question into a single standalone, search-optimized search query.
- Resolve any pronouns (it, that, them, they, those) to refer to the specific policies, benefits, or terms mentioned earlier in the conversation.
- Do NOT answer the question.
- Output ONLY the rewritten standalone query, with no commentary or quotes.

Conversation Summary:
{summary}

Recent History:
{history}

Latest Question: {query}
"""


async def rewriter_node(state: GraphState, config: RunnableConfig) -> dict:
    """
    Reformulates the user's input into a standalone search query using chat history & summary.
    """
    raw_query = state.get("raw_query", "").strip()
    messages = state.get("messages", [])
    summary = state.get("conversation_summary", "None") or "None"
    db = config.get("configurable", {}).get("db")

    # If there is no prior history or summary, the raw query is already standalone
    if not messages and (summary == "None" or not summary):
        return {"rewritten_query": raw_query}

    if not db:
        return {"rewritten_query": raw_query}

    try:
        fast_model = await LLMProviderFactory.get_fast_model(db=db, temperature=0.0)

        history_lines = [
            f"{'User' if m.type == 'human' else 'Assistant'}: {m.content[:150]}"
            for m in messages[-4:]  # Last 4 messages
        ]
        history_text = "\n".join(history_lines) if history_lines else "None"

        formatted_prompt = REWRITER_PROMPT.format(
            summary=summary,
            history=history_text,
            query=raw_query,
        )

        response = await fast_model.ainvoke([HumanMessage(content=formatted_prompt)])
        rewritten = response.content.strip().replace('"', '').replace("'", "")
        
        logger.info(f"Query rewritten: '{raw_query}' -> '{rewritten}'")
        return {"rewritten_query": rewritten or raw_query}

    except Exception as e:
        logger.warning(f"Query rewriter failed: {e}. Falling back to raw query.", exc_info=True)
        return {"rewritten_query": raw_query}
