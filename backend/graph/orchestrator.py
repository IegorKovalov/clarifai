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
    """Returns a polite message for off-topic questions."""
    message = "I'm here to help with questions about our products and services. Could you ask me something related to that?"
    messages = state.get("messages", [])
    messages.append({"role": "assistant", "content": message})
    return {"generation": message, "messages": messages}


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
        ("system", "Rewrite the customer question to be clearer and more likely to match relevant documents. Keep the same intent but use different wording."),
        ("human", "Original question: {question}\n\nRewrite it:")
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

    return graph.compile()


# Compiled graph — imported by FastAPI routes
clarifai_graph = build_graph()