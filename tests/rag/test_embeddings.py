from app.rag.embeddings import create_embedding


def test_create_embedding():
    embedding = create_embedding("машина")

    assert isinstance(embedding, list)
    assert len(embedding) == 1024
    assert all(isinstance(value, float) for value in embedding)
