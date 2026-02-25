from sqlalchemy import (
    Column, String, DateTime, Text, 
    Float, Boolean, Integer, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from db.database import Base
from datetime import datetime
import uuid


class Tenant(Base):
    """
    Represents a company using ClarifAI.
    Every other table links back to a tenant.
    """
    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    api_key = Column(String(255), unique=True, nullable=False)
    escalation_email = Column(String(255), nullable=True)
    bot_name = Column(String(100), default="Assistant")
    language = Column(String(10), default="en")
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships — lets you do tenant.documents instead of a separate query
    documents = relationship("Document", back_populates="tenant")
    conversations = relationship("Conversation", back_populates="tenant")


class Document(Base):
    """
    A file uploaded by a tenant for their knowledge base.
    The actual text content gets chunked into Embeddings.
    """
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50))
    status = Column(String(50), default="processing")
    chunk_count = Column(Integer, default=0)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    tenant = relationship("Tenant", back_populates="documents")
    embeddings = relationship("Embedding", back_populates="document")


class Embedding(Base):
    """
    A single text chunk from a document, stored as a vector.
    This is the table pgvector searches through.
    tenant_id here is the KEY to multi-tenancy isolation —
    every similarity search ALWAYS filters by this column.
    """
    __tablename__ = "embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    content = Column(Text, nullable=False)
    vector = Column(Vector(1536))
    chunk_index = Column(Integer)
    metadata_ = Column(Text)

    document = relationship("Document", back_populates="embeddings")


class Conversation(Base):
    """
    A support chat session between a customer and ClarifAI.
    Stores full message history, confidence scores, and feedback.
    """
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    session_id = Column(String(255), nullable=False)
    messages = Column(Text, default="[]")
    escalated = Column(Boolean, default=False)
    escalation_reason = Column(Text, nullable=True)
    confidence_scores = Column(Text, default="[]")
    feedback = Column(String(10), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tenant = relationship("Tenant", back_populates="conversations")
