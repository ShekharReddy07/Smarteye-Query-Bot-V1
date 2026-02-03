from fastapi import FastAPI
from pydantic import BaseModel
from core.query_runner import handle_question

app = FastAPI(title="SmartEye Backend API")

class QueryRequest(BaseModel):
    question: str
    mill: str = "hastings"

@app.post("/query")
def run_query(req: QueryRequest):
    """
    Receives question + mill from UI,
    processes it safely,
    and returns structured response.
    """
    return handle_question(req.question, req.mill)
