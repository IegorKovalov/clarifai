import logging
import uuid

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agents.memory import load_conversation, save_conversation
from api.dependencies import check_chat_rate_limit, get_tenant
from api.rate_limiter import chat_rate_limiter
from db.database import AsyncSessionLocal, get_db
from db.models import Tenant
from graph.orchestrator import clarifai_graph
from schemas.pydantic_models import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


def _build_initial_state(tenant_id: str, message: str, history: list) -> dict:
    return {
        "messages": history + [{"role": "user", "content": message}],
        "tenant_id": tenant_id,
        "question": message,
        "documents": [],
        "generation": "",
        "escalated": False,
        "rewrite_count": 0,
        "confidence_score": 0.0,
        "feedback": None,
        "decision": "vectorstore",
    }


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    tenant: Tenant = Depends(check_chat_rate_limit),
    db: AsyncSession = Depends(get_db),
):
    """REST chat — blocks until the full answer is ready."""
    session_id = request.session_id or str(uuid.uuid4())
    memory = await load_conversation(db, session_id, str(tenant.id))
    initial_state = _build_initial_state(str(tenant.id), request.message, memory["messages"])

    result = await clarifai_graph.ainvoke(initial_state)
    await save_conversation(db, session_id, str(tenant.id), result)

    return ChatResponse(
        session_id=session_id,
        answer=result["generation"],
        confidence_score=result["confidence_score"],
        escalated=result["escalated"],
    )


@router.websocket("/ws/{session_id}")
async def chat_ws(
    websocket: WebSocket,
    session_id: str,
    api_key: str = Query(...),
):
    """
    WebSocket chat with token-by-token streaming.
    Auth: pass the API key as ?api_key=sk_...
    
    Client sends:  {"message": "..."}
    Server streams: {"type": "token", "content": "..."}  (many)
    Server sends:   {"type": "done", "confidence": 0.92, "escalated": false}
    """
    await websocket.accept()

    async with AsyncSessionLocal() as db:
        # Auth
        result = await db.execute(
            select(Tenant).where(Tenant.api_key == api_key, Tenant.is_active == True)
        )
        tenant = result.scalar_one_or_none()
        if not tenant:
            await websocket.send_json({"type": "error", "content": "Invalid API key"})
            await websocket.close(code=1008)
            return

        try:
            while True:
                data = await websocket.receive_json()
                message = data.get("message", "").strip()
                if not message:
                    continue

                allowed, retry_after = chat_rate_limiter.check(str(tenant.id))
                if not allowed:
                    await websocket.send_json({
                        "type": "error",
                        "content": f"Rate limit exceeded. Retry after {retry_after} seconds.",
                    })
                    continue

                memory = await load_conversation(db, session_id, str(tenant.id))
                initial_state = _build_initial_state(
                    str(tenant.id), message, memory["messages"]
                )

                final_state = {}

                async for event in clarifai_graph.astream_events(initial_state, version="v2"):
                    # Stream tokens from the generate node only
                    if (
                        event["event"] == "on_chat_model_stream"
                        and event.get("metadata", {}).get("langgraph_node") == "generate"
                    ):
                        chunk = event["data"]["chunk"]
                        if chunk.content:
                            await websocket.send_json({
                                "type": "token",
                                "content": chunk.content,
                            })

                    # Capture final graph output
                    elif event["event"] == "on_chain_end" and event["name"] == "LangGraph":
                        final_state = event["data"].get("output", {})

                if final_state:
                    await save_conversation(db, session_id, str(tenant.id), final_state)

                await websocket.send_json({
                    "type": "done",
                    "confidence": final_state.get("confidence_score", 0.0),
                    "escalated": final_state.get("escalated", False),
                    "session_id": session_id,
                })

        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected: session {session_id}")
        except Exception as e:
            logger.error(f"WebSocket error (session {session_id}): {e}")
            try:
                await websocket.send_json({"type": "error", "content": "An internal error occurred"})
                await websocket.close(code=1011)
            except Exception:
                pass
