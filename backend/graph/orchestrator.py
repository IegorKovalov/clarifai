import logging
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, END
from sqlalchemy.ext.asyncio import AsyncSession

from agents.escalation import escalate
from agents.grader import grade_answer, grade_documents
from agents.memory import load_conversation, save_conversation
from agents.rag_agent import generate_answer, retrieve
from agents.router import route_question
from config import settings
from graph.state import ClarifAIState

logger = logging.getLogger(__name__)

CONFIDENCE_THRESHOLD = 0.7
MAX_REWRITES = 2


# --- Conditional edge functions ---
# These look at the state and return the name of the next node


def grade_documents_decision(state: ClarifAIState) -> str:
    """After grading documents — do we have relevant chunks?"""
    docs = state.get("documents", [])
    rewrite_count = state.get("rewrite_count", 0)

    if len(docs) == 0 and rewrite_count < MAX_REWRITES:
        return "rewrite"
    elif len(docs) == 0 and rewrite_count >= MAX_REWRITES:
        return "escalate"
    else:
        return "generate"


def grade_answer_decision(state: ClarifAIState) -> str:
    """After grading answer — are we confident enough?"""
    score = state.get("confidence_score", 0.0)
    if score >= CONFIDENCE_THRESHOLD:
        return "end"
    else:
        return "escalate"


# --- Off-topic handler ---

async def handle_off_topic(state: ClarifAIState) -> dict:
    """Returns a polite redirect for genuinely off-topic questions."""
    message = "That's a bit outside my area — I'm here to help with questions about our products and services. What can I help you with?"
    messages = state.get("messages", [])
    messages.append({"role": "assistant", "content": message})
    return {"generation": message, "messages": messages}


# --- Chitchat handler ---

async def handle_chitchat(state: ClarifAIState) -> dict:
    """Responds naturally to greetings and conversational messages using Claude."""
    from langchain_anthropic import ChatAnthropic
    from langchain_core.prompts import ChatPromptTemplate

    llm = ChatAnthropic(
        model="claude-haiku-4-5-20251001",
        api_key=settings.anthropic_api_key,
        temperature=0.7,
        streaming=True,
    )

    history = state.get("messages", [])
    history_text = ""
    for m in history[:-1]:  # exclude the current message
        role = "Customer" if m["role"] == "user" else "Assistant"
        history_text += f"{role}: {m['content']}\n"

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a friendly, warm customer support assistant. 
Respond naturally and conversationally to greetings and small talk.
Keep replies short (1-3 sentences). Be genuine, not robotic.
You can briefly mention that you're here to help with questions about products and services,
but don't be pushy about it. Just be a pleasant, helpful presence.

{history}"""),
        ("human", "{message}")
    ])

    chain = prompt | llm
    result = await chain.ainvoke({
        "history": f"Previous conversation:\n{history_text}" if history_text else "",
        "message": state["question"],
    })

    message = result.content
    messages = state.get("messages", [])
    messages.append({"role": "assistant", "content": message})
    return {"generation": message, "messages": messages, "confidence_score": 1.0}


# --- Rewrite question node ---

async def rewrite_question(state: ClarifAIState) -> dict:
    """Rewrites the question to improve retrieval."""
    from langchain_core.prompts import ChatPromptTemplate

    llm = ChatAnthropic(
        model="claude-haiku-4-5-20251001",
        api_key=settings.anthropic_api_key,
        temperature=0.3,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Rewrite the customer question to be clearer and more likely to match relevant documents. Keep the same intent but use different wording. Reply with ONLY the rewritten question — no explanations, no formatting, no quotes, no markdown."),
        ("human", "{question}")
    ])

    chain = prompt | llm
    result = await chain.ainvoke({"question": state["question"]})
    new_question = result.content

    logger.info(f"Rewrote question: {state['question']} → {new_question}")

    return {
        "question": new_question,
        "rewrite_count": state.get("rewrite_count", 0) + 1,
        "documents": [],  # clear old documents
    }


# --- Build the graph ---

def build_graph() -> StateGraph:
    graph = StateGraph(ClarifAIState)

    # Add all nodes
    graph.add_node("router", route_question)
    graph.add_node("retrieve", retrieve)
    graph.add_node("grade_documents", grade_documents)
    graph.add_node("rewrite_question", rewrite_question)
    graph.add_node("generate", generate_answer)
    graph.add_node("grade_answer", grade_answer)
    graph.add_node("escalate", escalate)
    graph.add_node("off_topic", handle_off_topic)
    graph.add_node("chitchat", handle_chitchat)

    # Entry point
    graph.set_entry_point("router")

    # Regular edges
    graph.add_edge("retrieve", "grade_documents")
    graph.add_edge("rewrite_question", "retrieve")
    graph.add_edge("generate", "grade_answer")

    # Conditional edge after grading documents
    graph.add_conditional_edges(
        "grade_documents",
        grade_documents_decision,
        {
            "generate": "generate",
            "rewrite": "rewrite_question",
            "escalate": "escalate",
        }
    )

    # Conditional edge after grading answer
    graph.add_conditional_edges(
        "grade_answer",
        grade_answer_decision,
        {
            "end": END,
            "escalate": "escalate",
        }
    )

    # Terminal nodes
    graph.add_edge("escalate", END)
    graph.add_edge("off_topic", END)
    graph.add_edge("chitchat", END)

    return graph.compile()


# Compiled graph — imported by FastAPI routes
clarifai_graph = build_graph()