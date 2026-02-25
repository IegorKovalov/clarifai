import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import ingest

# Configure logging — this makes all our logger.info() calls actually print
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)

app = FastAPI(
    title="ClarifAI",
    description="Multi-tenant AI customer support platform",
    version="0.1.0",
)

# CORS — allows the React frontend to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register the ingestion router
app.include_router(ingest.router, prefix="/api")


@app.get("/health")
async def health_check():
    """Simple endpoint to confirm the server is running."""
    return {"status": "ok", "service": "ClarifAI"}