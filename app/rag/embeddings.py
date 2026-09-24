import os

import httpx

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
