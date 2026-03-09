from pydantic import BaseModel, HttpUrl
from typing import Literal, Optional
from datetime import datetime
import uuid


# --- Tenant schemas ---

class TenantCreate(BaseModel):
    name: str
    escalation_email: Optional[str] = None
    bot_name: Optional[str] = "Assistant"


class TenantResponse(BaseModel):
    id: uuid.UUID
    name: str
    api_key: str
    escalation_email: Optional[str]
    bot_name: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# --- Chat schemas ---

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    confidence_score: float
    escalated: bool


# --- Feedback schemas ---

class FeedbackRequest(BaseModel):
    feedback: Literal["thumbs_up", "thumbs_down"]


# --- Admin schemas ---

class AdminStatsResponse(BaseModel):
    total_conversations: int
    escalated_conversations: int
    escalation_rate: float
    avg_confidence_score: float


# --- Ingestion schemas ---

class URLIngestRequest(BaseModel):
    url: HttpUrl


class DocumentResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    filename: str
    file_type: str
    status: str
    chunk_count: int
    uploaded_at: datetime

    class Config:
        from_attributes = True


class IngestResponse(BaseModel):
    document_id: uuid.UUID
    status: str
    message: str


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None