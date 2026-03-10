import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import admin, chat, ingest, tenants

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)

app = FastAPI(
    title="ClarifAI",
    description="Multi-tenant AI customer support platform",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tenants.router, prefix="/api")
app.include_router(ingest.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(admin.router, prefix="/api")


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "ClarifAI"}