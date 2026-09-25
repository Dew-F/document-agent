import os

import httpx
from sqlmodel import Session, select

from app.models import DocumentChunk

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://127.0.0.1:11434",
)

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "qwen3-embedding:0.6b",
)


def create_embedding(text: str) -> list[float]:
    response = httpx.post(
        f"{OLLAMA_BASE_URL}/api/embed",
        json={
            "model": EMBEDDING_MODEL,
            "input": text,
        },
        timeout=120,
    )

    response.raise_for_status()

    data = response.json()

    return data["embeddings"][0]


def embed_document(session: Session, document_id: int) -> None:
    statement = (
        select(DocumentChunk)
        .where(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index)
    )

    chunks = session.exec(statement).all()

    for chunk in chunks:
        chunk.embedding = create_embedding(chunk.content)

    session.commit()
