"""Optional FastAPI entrypoint for GitHub demonstration.

Run locally once dependencies are installed:
    uvicorn fastapi_app:app --reload
"""

from core import answer_query
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="RAG Knowledge Assistant Demo", version="1.0.0")


class QueryRequest(BaseModel):
    query: str
    top_k: int = 2


@app.get("/")
def root():
    return {
        "message": "RAG Knowledge Assistant Demo",
        "example": {
            "query": "How can we improve support efficiency while keeping knowledge accessible?"
        },
    }


@app.post("/query")
def query_assistant(payload: QueryRequest):
    return answer_query(payload.query, top_k=payload.top_k)
