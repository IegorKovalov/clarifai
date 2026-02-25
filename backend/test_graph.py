import asyncio
from graph.orchestrator import clarifai_graph
from db.database import AsyncSessionLocal

async def test():
    # Use the tenant and document we already ingested
    tenant_id = "3571cea2-79e0-48e6-92b7-a4a874ebe5e0"
    
    async with AsyncSessionLocal() as db:
        initial_state = {
            "messages": [{"role": "user", "content": "How can someone make a million dollars?"}],
            "tenant_id": tenant_id,
            "question": "How can someone make a million dollars?",
            "documents": [],
            "generation": "",
            "escalated": False,
            "rewrite_count": 0,
            "confidence_score": 0.0,
            "feedback": None,
        }

        result = await clarifai_graph.ainvoke(initial_state)

        print("\n--- RESULT ---")
        print(f"Answer: {result['generation']}")
        print(f"Confidence: {result['confidence_score']}")
        print(f"Escalated: {result['escalated']}")
        print(f"Rewrite count: {result['rewrite_count']}")

asyncio.run(test())