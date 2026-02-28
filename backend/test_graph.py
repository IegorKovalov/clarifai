# import asyncio
# from graph.orchestrator import clarifai_graph
# from db.database import AsyncSessionLocal

# async def test():
#     # Use the tenant and document we already ingested
#     tenant_id = "3571cea2-79e0-48e6-92b7-a4a874ebe5e0"
    
#     async with AsyncSessionLocal() as db:
#         initial_state = {
#             "messages": [{"role": "user", "content": "How can someone make a million dollars?"}],
#             "tenant_id": tenant_id,
#             "question": "How can someone make a million dollars?",
#             "documents": [],
#             "generation": "",
#             "escalated": False,
#             "rewrite_count": 0,
#             "confidence_score": 0.0,
#             "feedback": None,
#         }

#         result = await clarifai_graph.ainvoke(initial_state)

#         print("\n--- RESULT ---")
#         print(f"Answer: {result['generation']}")
#         print(f"Confidence: {result['confidence_score']}")
#         print(f"Escalated: {result['escalated']}")
#         print(f"Rewrite count: {result['rewrite_count']}")

# asyncio.run(test())

import asyncio
from graph.orchestrator import clarifai_graph

async def test(question: str, label: str):
    tenant_id = "3571cea2-79e0-48e6-92b7-a4a874ebe5e0"
    
    initial_state = {
        "messages": [{"role": "user", "content": question}],
        "tenant_id": tenant_id,
        "question": question,
        "documents": [],
        "generation": "",
        "escalated": False,
        "rewrite_count": 0,
        "confidence_score": 0.0,
        "feedback": None,
        "decision": "",
    }

    result = await clarifai_graph.ainvoke(initial_state)

    print(f"\n{'='*60}")
    print(f"TEST: {label}")
    print(f"QUESTION: {question}")
    print(f"ANSWER: {result['generation'][:200]}...")
    print(f"CONFIDENCE: {result['confidence_score']}")
    print(f"ESCALATED: {result['escalated']}")
    print(f"REWRITE COUNT: {result['rewrite_count']}")
    print(f"{'='*60}")


async def main():
    tests = [
        # Normal RAG — should answer confidently
        ("How can someone create wealth?", "NORMAL — should answer from knowledge base"),

        # Off-topic — should politely redirect
        ("What is the capital of France?", "OFF-TOPIC — should redirect"),

        # Escalation via router — customer explicitly asks for human
        ("I want to speak to a human agent right now", "ESCALATE VIA ROUTER — explicit request"),

        # Escalation via router — complaint/legal threat
        ("I'm going to sue your company for this terrible service", "ESCALATE VIA ROUTER — legal threat"),

        # Low confidence — question is on-topic but not in knowledge base
        ("What are your refund policies and pricing plans?", "LOW CONFIDENCE — not in knowledge base, should escalate"),

        # Vague question — may trigger rewrite
        ("tell me more", "VAGUE — may trigger rewrite"),
    ]

    for question, label in tests:
        await test(question, label)

asyncio.run(main())