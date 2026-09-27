import logging
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from app.services.llm.factory import LLMProviderFactory
from app.services.rag.workflow.state import GraphState

logger = logging.getLogger(__name__)

RAG_GENERATOR_PROMPT = """You are PolicyHelper, the dedicated internal policy assistant for company employees.

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


async def generator_node(state: GraphState, config: RunnableConfig) -> dict:
    """
    Synthesizes a policy answer grounded strictly on relevant retrieved chunks.
    """
    relevant_chunks = state.get("relevant_chunks", [])
    raw_query = state.get("raw_query", "")
    summary = state.get("conversation_summary")
    model_name = state.get("model_name")
    provider_name = state.get("provider_name")
    db = config.get("configurable", {}).get("db")

    if not db:
        return {
            "generation": "Database connection is unavailable.",
            "is_fallback": True,
        }

    # Format context blocks
    context_blocks = []
    for i, chunk in enumerate(relevant_chunks, 1):
        page_info = f", Page {chunk['page_number']}" if chunk.get('page_number') else ""
        context_blocks.append(
            f"--- Source [{i}]: {chunk['document_title']}{page_info} ---\n{chunk['content']}\n"
        )
    context_str = "\n".join(context_blocks) if context_blocks else "No matching policy documents found."

    system_instruction = RAG_GENERATOR_PROMPT.format(context=context_str)
    prompt_messages = [SystemMessage(content=system_instruction)]

    if summary:
        prompt_messages.append(SystemMessage(content=f"Prior conversation context summary:\n{summary}"))

    prompt_messages.append(HumanMessage(content=raw_query))

    try:
        chat_model = await LLMProviderFactory.get_chat_model(
            db=db,
            provider_name=provider_name,
            model_name=model_name,
            temperature=0.1,
            streaming=True,
        )

        response = await chat_model.ainvoke(prompt_messages)
        content_text = response.content if isinstance(response.content, str) else str(response.content)

        return {
            "generation": content_text,
            "is_fallback": False,
        }

    except Exception as e:
        logger.error(f"Error in generator_node: {e}", exc_info=True)
        return {
            "generation": "An error occurred while generating the policy response. Please try again.",
            "is_fallback": True,
        }
