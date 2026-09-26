import logging
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_core.messages import SystemMessage, HumanMessage

from app.core.database import AsyncSessionLocal
from app.models.chat import ChatSession
from app.services.llm.factory import get_llm_provider

logger = logging.getLogger(__name__)


async def generate_session_title_async(session_id: uuid.UUID, first_user_query: str) -> str | None:
    """
    Background worker:
    Summarizes the user's initial question into a concise 3-5 word title and updates chat_sessions table.
    """
    async with AsyncSessionLocal() as db:
        session = await db.get(ChatSession, session_id)
        if not session or session.is_title_auto_generated:
            return None

        try:
            llm_provider = get_llm_provider()
            fast_model = llm_provider.get_fast_model(temperature=0.3)

            prompt = (
                "You are an expert title generator for a corporate policy chatbot. "
                "Given the user's question, produce a concise, professional 3 to 5 word title. "
                "Do not use quotes, punctuation, or words like 'Query' or 'Question'.\n\n"
                f"User Question: {first_user_query.strip()}"
            )

            response = await fast_model.ainvoke([HumanMessage(content=prompt)])
            new_title = response.content.strip().replace('"', '').replace("'", "")
            if len(new_title) > 80:
                new_title = new_title[:77] + "..."

            if new_title:
                session.title = new_title
                session.is_title_auto_generated = True
                await db.commit()
                logger.info(f"Auto-generated title for session {session_id}: '{new_title}'")
                return new_title

        except Exception as e:
            logger.error(f"Failed to auto-generate session title for {session_id}: {e}", exc_info=True)

        return None
