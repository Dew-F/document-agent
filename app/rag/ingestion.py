from pathlib import Path

from sqlmodel import Session

from app.models import Document, DocumentChunk
from app.rag.chunking import chunk_markdown


def ingest_document(
    session: Session,
    path: Path,
    source: str,
    language: str,
    title: str,
) -> Document:
    text = path.read_text(encoding="utf-8")
    chunks = chunk_markdown(text)

    document = Document(
        source=source,
        language=language,
        path=str(path),
        title=title,
    )

    session.add(document)
    session.flush()

    for chunk_index, chunk in enumerate(chunks):
        document_chunk = DocumentChunk(
            document_id=document.id,
            content=chunk["content"],
            chunk_index=chunk_index,
            heading_path=chunk["heading_path"],
            token_count=None,
            embedding=None,
        )

        session.add(document_chunk)

    session.commit()
    session.refresh(document)

    return document
