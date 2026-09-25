import re

from sqlalchemy import String, cast, func, text
from sqlmodel import Session, select

from app.models import DocumentChunk
from app.rag.embeddings import create_embedding


def search_chunks(
    session: Session,
    query_embedding: list[float],
    limit: int = 3,
) -> list[tuple[DocumentChunk, float]]:
    distance_expression = DocumentChunk.embedding.cosine_distance(
        query_embedding
    ).label("distance")

    statement = (
        select(DocumentChunk, distance_expression)
        .where(DocumentChunk.embedding.is_not(None))
        .order_by(distance_expression)
        .limit(limit)
    )

    return session.exec(statement).all()


def search_text_chunks(
    session: Session,
    query: str,
    limit: int = 20,
) -> list[tuple[DocumentChunk, float]]:
    search_text = func.concat(
        cast(DocumentChunk.heading_path, String),
        " ",
        DocumentChunk.content,
    )

    search_vector = func.to_tsvector(
        "english",
        search_text,
    )

    terms = re.findall(r"\w+", query)

    if not terms:
        return []

    fts_query = " OR ".join(terms)

    search_query = func.websearch_to_tsquery(
        "english",
        fts_query,
    )

    rank = func.ts_rank(
        search_vector,
        search_query,
    ).label("rank")

    match = search_vector.op("@@")(search_query)

    statement = (
        select(DocumentChunk, rank)
        .where(
            DocumentChunk.embedding.is_not(None),
            match,
        )
        .order_by(rank.desc())
        .limit(limit)
    )

    return session.exec(statement).all()


def hybrid_search(
    session: Session,
    query: str,
    limit: int = 5,
    candidate_limit: int = 20,
    k: int = 60,
) -> list[tuple[DocumentChunk, float, int | None, int | None]]:
    query_embedding = create_embedding(query)

    vector_results = search_chunks(
        session=session,
        query_embedding=query_embedding,
        limit=candidate_limit,
    )

    text_results = search_text_chunks(
        session=session,
        query=query,
        limit=candidate_limit,
    )

    chunks: dict[int, DocumentChunk] = {}
    scores: dict[int, float] = {}
    vector_ranks: dict[int, int] = {}
    text_ranks: dict[int, int] = {}

    for rank, (chunk, _) in enumerate(vector_results, start=1):
        chunks[chunk.id] = chunk
        vector_ranks[chunk.id] = rank
        scores[chunk.id] = scores.get(chunk.id, 0) + 1 / (k + rank)

    for rank, (chunk, _) in enumerate(text_results, start=1):
        chunks[chunk.id] = chunk
        text_ranks[chunk.id] = rank
        scores[chunk.id] = scores.get(chunk.id, 0) + 1 / (k + rank)

    ranked_ids = sorted(
        scores,
        key=scores.get,
        reverse=True,
    )[:limit]

    return [
        (
            chunks[chunk_id],
            scores[chunk_id],
            vector_ranks.get(chunk_id),
            text_ranks.get(chunk_id),
        )
        for chunk_id in ranked_ids
    ]
