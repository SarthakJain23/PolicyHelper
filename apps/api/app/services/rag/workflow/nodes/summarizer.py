import logging
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from langchain_core.runnables import RunnableConfig
from app.services.llm.factory import LLMProviderFactory
from app.services.rag.workflow.state import GraphState

logger = logging.getLogger(__name__)

SLIDING_WINDOW_SIZE = 4  # Keep last 4 messages (2 user turns + 2 assistant turns)
SUMMARY_TRIGGER_THRESHOLD = 6  # Summarize when history exceeds 6 messages


async def summarizer_node(state: GraphState, config: RunnableConfig) -> dict:
    """
    Manages long conversation context and token budget:
    - Retains only the most recent K messages in the active window.
    - Condenses older messages into a rolling `conversation_summary` using a fast LLM.
    """
    messages = state.get("messages", [])
    current_summary = state.get("conversation_summary")

    if len(messages) <= SUMMARY_TRIGGER_THRESHOLD:
        return {
            "messages": messages,
            "conversation_summary": current_summary,
        }

    db = config.get("configurable", {}).get("db")
    if not db:
        return {"messages": messages[-SLIDING_WINDOW_SIZE:], "conversation_summary": current_summary}

    try:
        fast_model = await LLMProviderFactory.get_fast_model(db=db, temperature=0.2)
        
        # Messages to compress (all except the sliding window)
        messages_to_summarize = messages[:-SLIDING_WINDOW_SIZE]
        recent_messages = messages[-SLIDING_WINDOW_SIZE:]

        formatted_convo = "\n".join(
            f"{'User' if isinstance(m, HumanMessage) else 'Assistant'}: {m.content}"
            for m in messages_to_summarize
        )

        existing_summary_clause = (
            f"Existing Summary:\n{current_summary}\n\n" if current_summary else ""
        )

        prompt = (
            "You are an expert conversation summarizer for a corporate assistant. "
            "Update the conversation summary by incorporating the new messages below. "
            "Retain all critical facts: user constraints, policy topics discussed, and answers given. "
            "Keep the summary concise, objective, and under 200 words.\n\n"
            f"{existing_summary_clause}"
            f"New Messages to incorporate:\n{formatted_convo}"
        )

        response = await fast_model.ainvoke([HumanMessage(content=prompt)])
        new_summary = response.content.strip()

        logger.info(f"Updated conversation summary for session {state.get('session_id')}")
        return {
            "messages": recent_messages,
            "conversation_summary": new_summary,
        }

    except Exception as e:
        logger.warning(f"Summarizer failed gracefully: {e}. Truncating window only.")
        return {
            "messages": messages[-SLIDING_WINDOW_SIZE:],
            "conversation_summary": current_summary,
        }
