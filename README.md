# ClarifAI 🤖

> **B2B SaaS AI support platform** — companies upload their knowledge base (PDFs, URLs, docs) and their customers get instant, accurate AI-powered answers.

Built as a deliberate skills project to go beyond "make it work" and understand where RAG pipelines and multi-agent systems actually break in production.

---

## What It Does

ClarifAI lets a business connect their documentation once — and have an intelligent support agent handle customer queries automatically, with confidence-aware escalation to a human when the model isn't sure.

**Core flow:**
```
Document Upload → Ingestion Pipeline → pgvector Index
                                            ↓
Customer Query → Self-RAG Agent (LangGraph) → Confidence Scoring
                                            ↓
                              High confidence → Answer
                              Low confidence  → Human Escalation
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Agent Orchestration | LangGraph (Self-RAG pattern) |
| LLM | Anthropic Claude |
| Backend | FastAPI |
| Vector Store | PostgreSQL + pgvector |
| Embeddings | OpenAI / Sentence Transformers |
| Frontend | React + TypeScript |
| Real-time | WebSocket streaming |
| Auth & Isolation | Multi-tenant per-company isolation |

---

## Key Features

- **Self-RAG loop** — the agent evaluates its own retrieval quality and regenerates queries before answering, rather than blindly returning the first result
- **Confidence scoring** — every response carries a confidence signal; low-confidence answers trigger escalation instead of hallucinating
- **Human escalation** — seamless handoff to a human agent when the model reaches the edge of its knowledge
- **Document ingestion pipeline** — handles PDFs, URLs, and raw text; chunks, embeds, and indexes on upload
- **Multi-tenant isolation** — each company's knowledge base is fully isolated; no cross-tenant data leakage
- **WebSocket streaming** — responses stream token-by-token for a responsive UX

---

## Architecture Decisions & Production Gaps I Focused On

This project was built specifically to train AI engineering judgment, not just ship a demo. The most interesting problems were:

**Retrieval quality** — Naive top-k retrieval breaks on ambiguous queries. Self-RAG adds a reflection step where the model scores its own context before generating. Explored the tradeoff between retrieval rounds and latency.

**Chunking strategy** — Fixed-size chunking loses semantic context at boundaries. Tested sentence-aware chunking and overlap windows. The right strategy depends on document type (prose vs. structured data).

**Confidence vs. hallucination** — Getting a model to say "I don't know" reliably is harder than getting it to answer. Explored calibrated confidence scoring as a first-order production concern.

**Multi-tenancy at the DB layer** — Implemented row-level isolation in pgvector so a single Postgres instance serves multiple tenants without risk of cross-contamination.

**Latency under Self-RAG** — The reflection loop adds round-trips. Profiled where time was spent and where the quality gain justified the cost.

---

## Project Structure

```
clarifai/
├── backend/
│   ├── agents/          # LangGraph Self-RAG agent logic
│   ├── ingestion/       # Document processing & embedding pipeline
│   ├── api/             # FastAPI routes & WebSocket handlers
│   ├── db/              # pgvector schema, migrations, multi-tenant logic
│   └── services/        # Confidence scoring, escalation, Claude integration
└── frontend/
    ├── src/
    │   ├── components/  # Chat UI, document upload, escalation view
    │   └── hooks/       # WebSocket streaming hooks
    └── public/
```

---

## Running Locally

```bash
# Backend
cd backend
pip install -r requirements.txt
cp .env.example .env  # Add your Anthropic API key + DB connection string
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

**Required env vars:**
```
ANTHROPIC_API_KEY=
DATABASE_URL=postgresql://...
OPENAI_API_KEY=        # for embeddings (optional if using sentence-transformers)
```

---

## What I Learned

The gap between a working RAG demo and a production-ready pipeline is where this project lived. A few honest takeaways:

- Retrieval is the bottleneck — better chunking and re-ranking moves the needle more than prompt engineering
- Self-RAG meaningfully reduces hallucination but adds ~40-60% latency per query in the reflection loop
- Confidence thresholds need tuning per domain — a threshold that works for tech docs fails for legal text
- Multi-tenancy is an afterthought in most tutorials and a first-class concern in real deployments

---

## Background

Built by [Iegor Kovalov](https://github.com/IegorKovalov) — CS graduate (HIT), former IAF Aircrew Officer, AI Engineer.

Focused on LangGraph multi-agent systems, RAG pipelines, and production-grade AI backend engineering.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)](https://linkedin.com/in/iegor-kovalov)
