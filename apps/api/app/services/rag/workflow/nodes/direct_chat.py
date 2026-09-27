import logging
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from app.services.llm.factory import LLMProviderFactory
from app.services.rag.workflow.state import GraphState

logger = logging.getLogger(__name__)

DIRECT_CHAT_SYSTEM_PROMPT = """You are PolicyHelper, the dedicated, friendly, and professional internal policy assistant for company employees.

Your role:
- Respond politely and warmly to greetings, thanks, and conversational remarks.
- If the user asks who you are or what you can do, explain clearly that you are their internal company policy assistant, ready to help them look up and understand company policies (such as leave, remote work, expenses, benefits, IT security, and HR guidelines).
- Encourage the user to ask any questions they have about company policies.
- Keep responses concise, helpful, and professional.
"""


async def direct_chat_node(state: GraphState, config: RunnableConfig) -> dict:
    """
    Handles conversational interactions that do not require RAG retrieval.
    """
    raw_query = state.get("raw_query", "")
    model_name = state.get("model_name")
    provider_name = state.get("provider_name")
    messages = state.get("messages", [])
    summary = state.get("conversation_summary")
    db = config.get("configurable", {}).get("db")

    if not db:
        return {
            "generation": "Hello! I am PolicyHelper, your company policy assistant. How can I help you today?",
            "is_fallback": False,
            "citations": [],
        }

    try:
        chat_model = await LLMProviderFactory.get_chat_model(
            db=db,
            provider_name=provider_name,
            model_name=model_name,
            temperature=0.3,
            streaming=True,
        )

        prompt_messages = [SystemMessage(content=DIRECT_CHAT_SYSTEM_PROMPT)]
        
        if summary:
            prompt_messages.append(SystemMessage(content=f"Prior conversation context summary:\n{summary}"))

        # Add recent turns (excluding latest raw_query if already present)
        for msg in messages:
            if msg.content != raw_query:
                prompt_messages.append(msg)

        prompt_messages.append(HumanMessage(content=raw_query))

        response = await chat_model.ainvoke(prompt_messages)
        content_text = response.content if isinstance(response.content, str) else str(response.content)

        return {
            "generation": content_text,
            "is_fallback": False,
            "citations": [],
        }

    except Exception as e:
        logger.error(f"Error in direct_chat_node: {e}", exc_info=True)
        return {
            "generation": "Hello! I am PolicyHelper. Please feel free to ask any question regarding company policies and guidelines.",
            "is_fallback": False,
            "citations": [],
        }
