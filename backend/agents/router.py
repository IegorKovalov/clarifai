import logging
from typing import Literal
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langgraph.types import Command
from pydantic import BaseModel, Field
from config import settings
from graph.state import ClarifAIState

logger = logging.getLogger(__name__)

# Structured output schema — Literal constraint ensures only valid values are returned
class RouteDecision(BaseModel):
    decision: Literal["vectorstore", "escalate", "off_topic"] = Field(
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

- 'vectorstore': Use this for any question about business, finance, entrepreneurship, products, 
  services, policies, or any topic a company's knowledge base might plausibly cover. Also use 
  this for vague or follow-up questions like "tell me more" or "can you explain?". 
  When in doubt, default to this.

- 'escalate': Use this ONLY when the customer explicitly asks for a human/agent, makes a legal 
  threat, or expresses urgent distress. Examples: "I want to speak to a human", 
  "I'm going to sue you", "get me a manager".

- 'off_topic': Use this ONLY for questions with ZERO possible business relevance — pure 
  geography facts, weather, sports scores, entertainment trivia, or science unrelated to any 
  business topic. Examples: "What is the capital of France?", "Who won the World Cup?", 
  "What is the boiling point of water?".

Respond with only the decision field filled in."""),
    ("human", "Customer question: {question}")
])

# Chain: prompt → Claude → structured output
router_chain = router_prompt | structured_llm


async def route_question(state: ClarifAIState) -> Command[Literal["retrieve", "escalate", "off_topic"]]:
    """
    Node function — uses Command to directly specify the next node,
    bypassing the need to store the decision in state.
    """
    logger.info(f"Routing question for tenant {state['tenant_id']}: {state['question']}")

    result = await router_chain.ainvoke({"question": state["question"]})
    decision = result.decision.strip().lower()

    goto = {"off_topic": "off_topic", "escalate": "escalate"}.get(decision, "retrieve")

    logger.info(f"Router decision: {decision} → goto: {goto}")
    return Command(goto=goto, update={"decision": decision})