from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime
import uuid


# --- Request schemas (what the API receives) ---

class URLIngestRequest(BaseModel):
    """Sent by the client when ingesting a URL"""
    url: HttpUrl
    tenant_id: uuid.UUID


# --- Response schemas (what the API returns) ---

class DocumentResponse(BaseModel):
    """Returned after a document is successfully ingested"""
    id: uuid.UUID
    tenant_id: uuid.UUID
    filename: str
    file_type: str
    status: str
    chunk_count: int
    uploaded_at: datetime

    class Config:
        from_attributes = True  # allows converting SQLAlchemy model → Pydantic


class IngestResponse(BaseModel):
    """Returned immediately when ingestion starts"""
    document_id: uuid.UUID
    status: str
    message: str


class ErrorResponse(BaseModel):
    """Returned when something goes wrong"""
    error: str
    detail: Optional[str] = None