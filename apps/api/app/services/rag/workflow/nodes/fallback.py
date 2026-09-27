import logging
from app.services.rag.workflow.state import GraphState

logger = logging.getLogger(__name__)


async def fallback_node(state: GraphState) -> dict:
    """
    Produces a polite, policy-compliant disclaimer when no relevant documents are indexed.
    """
    return {
        "generation": (
            "I could not find information regarding this in the company's uploaded policy documents. "
            "Please consult HR or your department lead directly for official guidance on this matter."
        ),
        "is_fallback": True,
        "citations": [],
    }
