import logging
from typing import Literal
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from app.services.llm.factory import LLMProviderFactory
from app.services.rag.workflow.state import GraphState

logger = logging.getLogger(__name__)


class GradeDocument(BaseModel):
    is_relevant: bool = Field(
        description="True if the context document contains information useful to answer the user query, False otherwise."
    )


GRADER_SYSTEM_PROMPT = """You are a relevance grader evaluating whether a retrieved document chunk is helpful and relevant to the user query.

Give a binary score:
- True: The chunk contains facts, policies, rules, or information related to the question.
- False: The chunk is unrelated noise, generic text, or does not address the question.
"""


async def grader_node(state: GraphState, config: RunnableConfig) -> dict:
    """
    Evaluates retrieved chunks for relevance to filter out noise.
    """
    retrieved_chunks = state.get("retrieved_chunks", [])
    query = state.get("rewritten_query") or state.get("raw_query", "")
    db = config.get("configurable", {}).get("db")

    if not retrieved_chunks:
        return {"relevant_chunks": []}

    # If score from hybrid retriever is high, accept directly to reduce latency
    high_confidence_chunks = [c for c in retrieved_chunks if c.get("score", 0) >= 0.65]
    if high_confidence_chunks:
        return {"relevant_chunks": retrieved_chunks}

    if not db:
        return {"relevant_chunks": retrieved_chunks}

    try:
        fast_model = await LLMProviderFactory.get_fast_model(db=db, temperature=0.0)
        structured_grader = fast_model.with_structured_output(GradeDocument)

        relevant: list[dict] = []
        for chunk in retrieved_chunks:
            prompt = f"User Query: {query}\n\nDocument Chunk Content:\n{chunk['content'][:500]}"
            grade: GradeDocument = await structured_grader.ainvoke([
                SystemMessage(content=GRADER_SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ])
            if grade.is_relevant:
                relevant.append(chunk)

        logger.info(f"Grader filtered chunks: {len(relevant)}/{len(retrieved_chunks)} deemed relevant")
        return {"relevant_chunks": relevant}

    except Exception as e:
        logger.warning(f"Document grader failed: {e}. Keeping all chunks as fallback.", exc_info=True)
        return {"relevant_chunks": retrieved_chunks}
