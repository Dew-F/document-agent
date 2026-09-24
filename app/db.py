import os

from sqlmodel import Session, create_engine

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://document_agent:document_agent@127.0.0.1:5432/document_agent",
)

engine = create_engine(DATABASE_URL)


def get_session():
    with Session(engine) as session:
        yield session
