import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from api.dependencies import get_tenant
from db.database import get_db
from db.models import Conversation, Tenant
from schemas.pydantic_models import AdminStatsResponse, FeedbackRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats", response_model=AdminStatsResponse)
async def get_stats(
    tenant: Tenant = Depends(get_tenant),
    db: AsyncSession = Depends(get_db),
):
    """Returns conversation stats for the authenticated tenant."""
    result = await db.execute(
        select(Conversation).where(Conversation.tenant_id == tenant.id)
    )
    conversations = result.scalars().all()

    total = len(conversations)
    escalated_count = sum(1 for c in conversations if c.escalated)

    all_scores = []
    for c in conversations:
        scores = json.loads(c.confidence_scores or "[]")
        all_scores.extend(scores)

    avg_confidence = round(sum(all_scores) / len(all_scores), 3) if all_scores else 0.0
    escalation_rate = round(escalated_count / total, 3) if total > 0 else 0.0

    return AdminStatsResponse(
        total_conversations=total,
        escalated_conversations=escalated_count,
        escalation_rate=escalation_rate,
        avg_confidence_score=avg_confidence,
    )


@router.post("/feedback/{session_id}")
async def submit_feedback(
    session_id: str,
    request: FeedbackRequest,
    tenant: Tenant = Depends(get_tenant),
    db: AsyncSession = Depends(get_db),
):
    """Record thumbs_up / thumbs_down for a conversation."""
    result = await db.execute(
        select(Conversation).where(
            Conversation.session_id == session_id,
            Conversation.tenant_id == tenant.id,
        )
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conversation.feedback = request.feedback
    await db.commit()
    logger.info(f"Feedback '{request.feedback}' recorded for session {session_id}")
    return {"status": "ok"}
