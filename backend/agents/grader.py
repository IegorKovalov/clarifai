import logging
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from config import settings
from graph.state import ClarifAIState

logger = logging.getLogger(__name__)

# --- Structured output schemas ---

class DocumentGrade(BaseModel):
    relevant: str = Field(description="Is the document relevant to the question? 'yes' or 'no'")

class AnswerGrade(BaseModel):
    confidence_score: float = Field(
        description="Confidence score between 0.0 and 1.0. How well does the answer address the question based on the documents?"
    )

# --- LLM ---

llm = ChatAnthropic(
    model="claude-haiku-4-5-20251001",
    api_key=settings.anthropic_api_key,
    temperature=0,
)

document_grader_llm = llm.with_structured_output(DocumentGrade)
answer_grader_llm = llm.with_structured_output(AnswerGrade)

# --- Prompts ---

document_grade_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a document relevance grader.
    
Given a customer question and a retrieved document chunk, determine if the chunk 
contains information that is relevant to answering the question.

Be generous — if the chunk has ANY useful information, grade it as relevant.
Only grade as 'no' if the chunk is completely unrelated."""),
    ("human", "Question: {question}\n\nDocument chunk:\n{document}")
])

answer_grade_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an answer quality grader for a customer support system.

Given a question, the source documents, and a generated answer, score how confident 
you are that the answer correctly and completely addresses the question.

Score 0.8-1.0: Answer is complete, accurate, and directly addresses the question
Score 0.5-0.7: Answer is partially helpful but missing some details
Score 0.0-0.4: Answer is vague, incorrect, or doesn't address the question

The escalation threshold is 0.7 — answers below this will be escalated to a human."""),
    ("human", "Question: {question}\n\nSource documents:\n{documents}\n\nGenerated answer:\n{answer}")
])

# --- Chains ---

document_grade_chain = document_grade_prompt | document_grader_llm
answer_grade_chain = answer_grade_prompt | answer_grader_llm


# --- Node functions ---

async def grade_documents(state: ClarifAIState) -> dict:
    """
    Filters retrieved documents — keeps only relevant chunks.
    If no relevant chunks found, signals the orchestrator to rewrite the question.
    """
    logger.info(f"Grading {len(state['documents'])} documents for tenant {state['tenant_id']}")

    relevant_docs = []
    for doc in state["documents"]:
        result = await document_grade_chain.ainvoke({
            "question": state["question"],
            "document": doc["content"]
        })
        if result.relevant.strip().lower() == "yes":
            relevant_docs.append(doc)

    logger.info(f"Kept {len(relevant_docs)} relevant documents out of {len(state['documents'])}")
    return {"documents": relevant_docs}


async def grade_answer(state: ClarifAIState) -> dict:
    """
    Grades the generated answer — sets confidence_score.
    Orchestrator uses this to decide: END or escalate.
    """
    logger.info(f"Grading answer for tenant {state['tenant_id']}")

    docs_text = "\n\n".join([doc["content"] for doc in state["documents"]])

    result = await answer_grade_chain.ainvoke({
        "question": state["question"],
        "documents": docs_text,
        "answer": state["generation"]
    })

    score = round(result.confidence_score, 2)
    logger.info(f"Answer confidence score: {score}")
    return {"confidence_score": score}