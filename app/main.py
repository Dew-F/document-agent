from fastapi import FastAPI

app = FastAPI(title="Document Agent")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
