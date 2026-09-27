import logging
from typing import Literal
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from app.services.llm.factory import LLMProviderFactory
from app.services.rag.workflow.state import GraphState

logger = logging.getLogger(__name__)


class IntentClassification(BaseModel):
    intent: Literal["rag", "direct_chat"] = Field(
        description=(
            "Categorize intent: 'rag' if the question requires retrieving company policy documents, "
            "or 'direct_chat' for greetings, identity/capability inquiries, or generic pleasantries."
        )
    )
    confidence: float = Field(default=1.0, description="Confidence score 0.0 to 1.0")


ROUTER_PROMPT = """You are an intent classifier for PolicyHelper, an internal company policy assistant.

Determine whether the user's query requires:
- 'rag': The query is asking about company policies, rules, benefits, leave, work hours, IT guidelines, compliance, insurance, expenses, travel allowance, etc.
- 'direct_chat': The query is a greeting, polite pleasantry ("hello", "thanks", "how are you?"), or questions about the assistant itself ("who are you?", "what can you help me with?").

Classify the intent strictly as 'rag' or 'direct_chat'.
"""


async def router_node(state: GraphState, config: RunnableConfig) -> dict:
    """
    Routes user query to either RAG policy retrieval or direct conversational chat.
    """
    raw_query = state.get("raw_query", "").strip()
    db = config.get("configurable", {}).get("db")

    # Fast heuristic check for common greetings
    lower_query = raw_query.lower()
    if lower_query in ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "thanks", "thank you", "who are you?", "what can you do?"]:
        return {"intent": "direct_chat"}

    if not db:
        return {"intent": "rag"}

    try:
        fast_model = await LLMProviderFactory.get_fast_model(db=db, temperature=0.0)
        structured_model = fast_model.with_structured_output(IntentClassification)

        classification: IntentClassification = await structured_model.ainvoke([
            SystemMessage(content=ROUTER_PROMPT),
            HumanMessage(content=f"User Query: {raw_query}"),
        ])

        logger.info(f"Router classified query as '{classification.intent}' (confidence: {classification.confidence})")
        return {"intent": classification.intent}

    except Exception as e:
        logger.warning(f"Router classification error: {e}. Defaulting to 'rag'.", exc_info=True)
        return {"intent": "rag"}
