from typing import Optional, TypedDict


class ClarifAIState(TypedDict):
    """
    The state object that travels through every node in the graph.
    Every node reads from this and writes back to it.
    tenant_id is never optional — it ensures multi-tenant isolation.
    """
    messages: list          # full conversation history
    tenant_id: str          # never changes — filters every DB query
    question: str           # current customer question
    documents: list         # retrieved chunks from vector store
    generation: str         # Claude's generated answer
    escalated: bool         # whether this conversation was escalated
    rewrite_count: int      # how many times we've rewritten the question (max 2)
    confidence_score: float # how confident Claude is in the answer (0.0 - 1.0)
    feedback: Optional[str]          # 👍👎 from the customer after the conversation
    decision: str                    # router decision: 'vectorstore', 'escalate', 'off_topic', 'chitchat'
    escalation_email: Optional[str]  # tenant's escalation email — set at graph entry
