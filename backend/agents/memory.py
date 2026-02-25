import json
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models import Conversation
from graph.state import ClarifAIState
import uuid

logger = logging.getLogger(__name__)


async def load_conversation(
    db: AsyncSession,
    session_id: str,
    tenant_id: str,
) -> dict:
    """
    Loads existing conversation from DB if it exists.
    Returns messages history and other conversation data.
    """
    result = await db.execute(
        select(Conversation).where(
            Conversation.session_id == session_id,
            Conversation.tenant_id == uuid.UUID(tenant_id),
        )
    )
    conversation = result.scalar_one_or_none()

    if conversation:
        messages = json.loads(conversation.messages or "[]")
        confidence_scores = json.loads(conversation.confidence_scores or "[]")
        logger.info(f"Loaded conversation {session_id} with {len(messages)} messages")
        return {
            "messages": messages,
            "confidence_scores": confidence_scores,
            "escalated": conversation.escalated,
        }

    logger.info(f"No existing conversation found for session {session_id}")
    return {
        "messages": [],
        "confidence_scores": [],
        "escalated": False,
    }


async def save_conversation(
    db: AsyncSession,
    session_id: str,
    tenant_id: str,
    state: ClarifAIState,
) -> None:
    """
    Saves or updates the conversation in DB after each turn.
    """
    result = await db.execute(
        select(Conversation).where(
            Conversation.session_id == session_id,
            Conversation.tenant_id == uuid.UUID(tenant_id),
        )
    )
    conversation = result.scalar_one_or_none()

    # Append latest confidence score to history
    scores = json.loads(conversation.confidence_scores if conversation else "[]") if conversation else []
    if state.get("confidence_score"):
        scores.append(state["confidence_score"])

    if conversation:
        # Update existing conversation
        conversation.messages = json.dumps(state.get("messages", []))
        conversation.confidence_scores = json.dumps(scores)
        conversation.escalated = state.get("escalated", False)
        conversation.escalation_reason = "low_confidence" if state.get("escalated") else None
        conversation.feedback = state.get("feedback")
    else:
        # Create new conversation
        conversation = Conversation(
            id=uuid.uuid4(),
            tenant_id=uuid.UUID(tenant_id),
            session_id=session_id,
            messages=json.dumps(state.get("messages", [])),
            confidence_scores=json.dumps(scores),
            escalated=state.get("escalated", False),
            escalation_reason="low_confidence" if state.get("escalated") else None,
            feedback=state.get("feedback"),
        )
        db.add(conversation)

    await db.commit()
    logger.info(f"Saved conversation {session_id} for tenant {tenant_id}")