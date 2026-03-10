import logging
import uuid
from typing import Optional
import httpx
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import AsyncOpenAI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from db.models import Document, Embedding

# Set up logging so we can see what's happening in the terminal
logger = logging.getLogger(__name__)

# OpenAI client for embeddings
openai_client = AsyncOpenAI(api_key=settings.openai_api_key)

# Text splitter — 1000 chars per chunk, 200 overlap
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)


async def embed_text(text: str) -> list[float]:
    """Convert a string into a 1536-dimensional vector using OpenAI."""
    response = await openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return response.data[0].embedding


async def chunk_and_store(
    db: AsyncSession,
    document: Document,
    raw_text: str,
) -> int:
    """
    Takes raw extracted text, splits it into chunks,
    embeds each chunk, and stores them in the embeddings table.
    Returns the number of chunks created.
    """
    logger.info(f"Chunking document {document.id} — text length: {len(raw_text)}")

    chunks = text_splitter.split_text(raw_text)
    logger.info(f"Split into {len(chunks)} chunks")

    for i, chunk in enumerate(chunks):
        vector = await embed_text(chunk)

        embedding = Embedding(
            id=uuid.uuid4(),
            tenant_id=document.tenant_id,
            document_id=document.id,
            content=chunk,
            vector=vector,
            chunk_index=i,
        )
        db.add(embedding)

    await db.commit()
    logger.info(f"Stored {len(chunks)} embeddings for document {document.id}")
    return len(chunks)


async def search_similar(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    query: str,
    limit: int = 5,
) -> list[dict]:
    """
    Embeds the query, then searches for the most similar
    chunks in the embeddings table — filtered by tenant_id.
    Returns a list of the top matching chunks with their content.
    """
    logger.info(f"Searching embeddings for tenant {tenant_id}")

    query_vector = await embed_text(query)
    query_vector_str = "[" + ",".join(map(str, query_vector)) + "]"


    # pgvector cosine similarity search — <=> is the cosine distance operator
    # Lower distance = more similar, so we ORDER BY ASC
    result = await db.execute(
        text(f"""
            SELECT content, chunk_index, document_id,
                1 - (vector <=> '{query_vector_str}'::vector) AS similarity
            FROM embeddings
            WHERE tenant_id = '{str(tenant_id)}'::uuid
            ORDER BY vector <=> '{query_vector_str}'::vector
            LIMIT {limit}
        """)
    )

    rows = result.fetchall()
    return [
        {
            "content": row.content,
            "chunk_index": row.chunk_index,
            "document_id": str(row.document_id),
            "similarity": round(row.similarity, 4),
        }
        for row in rows
    ]


async def extract_text_from_url(url: str) -> str:
    """
    Fetch a URL and return clean text via Jina.ai Reader.
    Handles both static HTML and JavaScript-rendered pages,
    and bypasses bot protection that blocks raw HTTP scrapers.
    """
    jina_url = f"https://r.jina.ai/{url}"
    logger.info(f"Fetching via Jina Reader: {url}")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            jina_url,
            headers={"Accept": "text/plain"},
            follow_redirects=True,
            timeout=60,
        )
        response.raise_for_status()

    text = response.text
    logger.info(f"Extracted {len(text)} characters from URL")
    return text