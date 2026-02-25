import logging
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from config import settings
from graph.state import ClarifAIState

logger = logging.getLogger(__name__)

# Structured output schema — forces Claude to respond with exactly one of three values
class RouteDecision(BaseModel):
    decision: str = Field(
        description="Route the question to one of: 'vectorstore', 'escalate', 'off_topic'"
    )

# Claude model — we use claude-3-5-haiku for speed and cost on routing
llm = ChatAnthropic(
    model="claude-haiku-4-5-20251001",
    api_key=settings.anthropic_api_key,
    temperature=0,  # zero temperature = deterministic, no creativity needed here
)

# Bind structured output — Claude MUST respond with RouteDecision schema
structured_llm = llm.with_structured_output(RouteDecision)

# The routing prompt
router_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a router for a customer support AI system.
    
Your job is to classify the customer's question into exactly one of three categories:

- 'vectorstore': The question is about the company's products, services, policies, or anything 
  the knowledge base might answer. Default to this when unsure.
- 'escalate': The question involves a complaint, legal threat, urgent issue, or the customer 
  explicitly asks for a human agent.
- 'off_topic': The question is completely unrelated to customer support 
  (e.g. asking about the weather, general knowledge questions).

Respond with only the decision field filled in."""),
    ("human", "Customer question: {question}")
])

# Chain: prompt → Claude → structured output
router_chain = router_prompt | structured_llm


async def route_question(state: ClarifAIState) -> dict:
    """
    Node function — receives state, returns updated state.
    Decides where to route the customer's question.
    """
    logger.info(f"Routing question for tenant {state['tenant_id']}: {state['question']}")

    result = await router_chain.ainvoke({"question": state["question"]})
    decision = result.decision.strip().lower()

    logger.info(f"Router decision: {decision}")

    # We don't update state here — just return the decision
    # The orchestrator uses this to pick the next edge
    return {"decision": decision}