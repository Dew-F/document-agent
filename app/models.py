from sqlmodel import Field, SQLModel
from sqlalchemy import JSON
from pgvector.sqlalchemy import VECTOR


class Document(SQLModel, table=True):
    __tablename__ = "documents"

    id: int | None = Field(default=None, primary_key=True)

    source: str = Field(index=True)
    language: str = Field(index=True)

    path: str
    title: str | None = None


class DocumentChunk(SQLModel, table=True):
    __tablename__ = "document_chunks"

    id: int | None = Field(default=None, primary_key=True)

    document_id: int = Field(
        foreign_key="documents.id",
        index=True,
    )

    content: str
    chunk_index: int

    heading_path: list[str] = Field(
        default_factory=list,
        sa_type=JSON,
    )

    token_count: int | None = None

    embedding: list[float] | None = Field(
        default=None,
        sa_type=VECTOR(1024),
    )
