from fastapi import FastAPI
from pydantic import BaseModel
from search import search as search_func
from ingest import ingest as ingest_func

class SearchModel(BaseModel):
    log: str
    k: int | None = 3

class IngestModel(BaseModel):
    path: str

app = FastAPI()

@app.post("/search")
def search(search: SearchModel):
    return search_func(search.log, search.k)

@app.post("/ingest")
def ingest(ingest: IngestModel):
    ingest_func(ingest.path)
    return {"status": "ok", "path": ingest.path}

