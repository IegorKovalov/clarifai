import logging
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from config import settings
from db.vector_store import search_similar
from db.database import AsyncSessionLocal
from graph.state import ClarifAIState

logger = logging.getLogger(__name__)

llm = ChatAnthropic(
    model="claude-sonnet-4-6",  # Sonnet for generation — better quality
    api_key=settings.anthropic_api_key,
    temperature=0.3,  # slight creativity for natural answers
)

generate_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful customer support assistant.

Answer the customer's question using ONLY the information provided in the source documents below.
Be concise, friendly, and accurate.

If the documents don't contain enough information to fully answer the question, 
say what you do know and acknowledge the limitation honestly.

Source documents:
{documents}"""),
    ("human", "{question}")
])

generate_chain = generate_prompt | llm


async def retrieve(state: ClarifAIState) -> dict:
    """
    Retrieves relevant chunks from the vector store for this tenant.
    """
    logger.info(f"Retrieving documents for tenant {state['tenant_id']}")

    async with AsyncSessionLocal() as db:
        docs = await search_similar(
            db=db,
            tenant_id=state["tenant_id"],
            query=state["question"],
            limit=5,
        )

    logger.info(f"Retrieved {len(docs)} chunks")
    return {"documents": docs}


async def generate_answer(state: ClarifAIState) -> dict:
    """
    Generates an answer using retrieved documents as context.
    """
    logger.info(f"Generating answer for tenant {state['tenant_id']}")

    docs_text = "\n\n".join([doc["content"] for doc in state["documents"]])

    result = await generate_chain.ainvoke({
        "documents": docs_text,
        "question": state["question"],
    })

    generation = result.content
    logger.info(f"Generated answer: {generation[:100]}...")

    # Add to messages history
    messages = state.get("messages", [])
    messages.append({"role": "assistant", "content": generation})

    return {"generation": generation, "messages": messages}