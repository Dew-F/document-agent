import os

import httpx
from sqlmodel import Session, select

from app.db import engine
from app.models import Document, DocumentChunk
from app.rag.embeddings import create_embedding


def main() -> None:
    test_source = "embedding-test"

    with Session(engine) as session:
        # Удаляем предыдущий запуск эксперимента.
        documents = session.exec(
            select(Document).where(Document.source == test_source)
        ).all()

        for document in documents:
            chunks = session.exec(
                select(DocumentChunk).where(DocumentChunk.document_id == document.id)
            ).all()

            for chunk in chunks:
                session.delete(chunk)

            session.delete(document)

        session.commit()

        # Создаём один тестовый Document.
        document = Document(
            source=test_source,
            language="ru",
            path="internal://embedding-test",
            title="Embedding test",
        )

        session.add(document)
        session.commit()
        session.refresh(document)

        print(f"Created document: {document.id}")

        texts = [
            "Автомобиль движется по дороге.",
            "Легковой автомобиль припаркован возле дома.",
            "Рецепт борща содержит свёклу, капусту и картофель.",
        ]

        # Создаём chunks и получаем для каждого embedding.
        for index, text in enumerate(texts):
            embedding = create_embedding(text)

            chunk = DocumentChunk(
                document_id=document.id,
                content=text,
                chunk_index=index,
                heading_path=[],
                token_count=None,
                embedding=embedding,
            )

            session.add(chunk)

        session.commit()

        # Теперь ищем документы по смыслу.
        query = "машина"
        query_embedding = create_embedding(query)

        distance_expression = DocumentChunk.embedding.cosine_distance(query_embedding)

        statement = (
            select(DocumentChunk, distance_expression.label("distance"))
            .where(DocumentChunk.document_id == document.id)
            .order_by(distance_expression)
            .limit(3)
        )

        results = session.exec(statement).all()

        print(f"\nQuery: {query}")
        print("Results:")

        for chunk, distance in results:
            print(f"  distance={distance:.4f} | {chunk.content}")


if __name__ == "__main__":
    main()
