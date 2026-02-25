import logging
import uuid
from pathlib import Path

import pypdf
import docx
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from db.models import Document
from db.vector_store import chunk_and_store, extract_text_from_url
from schemas.pydantic_models import DocumentResponse, IngestResponse, URLIngestRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ingest", tags=["ingestion"])


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract plain text from a PDF file."""
    import io
    reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    logger.info(f"Extracted {len(text)} characters from PDF")
    return text


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract plain text from a Word document."""
    import io
    doc = docx.Document(io.BytesIO(file_bytes))
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    logger.info(f"Extracted {len(text)} characters from DOCX")
    return text


@router.post("/file", response_model=IngestResponse)
async def ingest_file(
    tenant_id: uuid.UUID = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a PDF or Word document for a tenant.
    Extracts text, chunks it, embeds it, and stores in the DB.
    """
    logger.info(f"File upload received: {file.filename} for tenant {tenant_id}")

    # Validate file type
    suffix = Path(file.filename).suffix.lower()
    if suffix not in [".pdf", ".docx"]:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")

    # Read file bytes
    file_bytes = await file.read()

    # Extract text based on file type
    if suffix == ".pdf":
        raw_text = extract_text_from_pdf(file_bytes)
    else:
        raw_text = extract_text_from_docx(file_bytes)

    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from file")

    # Create document record in DB
    document = Document(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        filename=file.filename,
        file_type=suffix.lstrip("."),
        status="processing",
        chunk_count=0,
    )
    db.add(document)
    await db.flush()  # gets the document ID without committing yet

    # Chunk, embed, and store
    chunk_count = await chunk_and_store(db, document, raw_text)

    # Update document status
    document.status = "complete"
    document.chunk_count = chunk_count
    await db.commit()

    logger.info(f"Ingestion complete: {chunk_count} chunks for document {document.id}")

    return IngestResponse(
        document_id=document.id,
        status="complete",
        message=f"Successfully ingested {chunk_count} chunks",
    )


@router.post("/url", response_model=IngestResponse)
async def ingest_url(
    request: URLIngestRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Ingest a URL for a tenant.
    Fetches the page, extracts text, chunks, embeds, and stores.
    """
    logger.info(f"URL ingestion received: {request.url} for tenant {request.tenant_id}")

    # Fetch and extract text from URL
    raw_text = await extract_text_from_url(str(request.url))

    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from URL")

    # Use URL as filename
    document = Document(
        id=uuid.uuid4(),
        tenant_id=request.tenant_id,
        filename=str(request.url),
        file_type="url",
        status="processing",
        chunk_count=0,
    )
    db.add(document)
    await db.flush()

    chunk_count = await chunk_and_store(db, document, raw_text)

    document.status = "complete"
    document.chunk_count = chunk_count
    await db.commit()

    return IngestResponse(
        document_id=document.id,
        status="complete",
        message=f"Successfully ingested {chunk_count} chunks from URL",
    )