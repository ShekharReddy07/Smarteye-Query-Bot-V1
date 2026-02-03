from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd

from core.query_runner import handle_question
from core.db import (
    get_employees_by_date_range,
    get_monthwise_attendance
)

app = FastAPI(title="SmartEye Backend API")

# ============================================================
# REQUEST MODELS
# ============================================================

class QueryRequest(BaseModel):
    question: str
    mill: str = "hastings"


class EmployeeRequest(BaseModel):
    mill: str
    start_date: str
    end_date: str


class MonthwiseAttendanceRequest(BaseModel):
    mill: str
    start_date: str
    end_date: str
    ecode: str


# ============================================================
# HELPERS
# ============================================================

def make_json_safe(obj):
    """
    Converts Pandas / NumPy objects into JSON-safe Python types
    """
    if isinstance(obj, pd.DataFrame):
        return obj.astype(object).where(pd.notnull(obj), None).to_dict(orient="records")

    if isinstance(obj, dict):
        return {k: make_json_safe(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return [make_json_safe(v) for v in obj]

    return obj


# ============================================================
# QUERY ENDPOINT (LLM-BASED)
# ============================================================

@app.post("/query")
def run_query(req: QueryRequest):
    """
    Receives question + mill from UI,
    processes it safely,
    and returns structured JSON response.
    """
    try:
        result = handle_question(req.question, req.mill)
        return make_json_safe(result)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# EMPLOYEE LIST ENDPOINT (NO LLM)
# ============================================================

@app.post("/employees")
def get_employees(req: EmployeeRequest):
    """
    Returns list of employees for a given date range.
    """
    try:
        data = get_employees_by_date_range(
            req.mill,
            req.start_date,
            req.end_date
        )
        return make_json_safe(data)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# MONTH-WISE ATTENDANCE ENDPOINT (NO LLM)
# ============================================================

@app.post("/monthwise-attendance")
def monthwise_attendance(req: MonthwiseAttendanceRequest):
    """
    Returns month-wise attendance for a selected employee.
    """
    try:
        data = get_monthwise_attendance(
            req.mill,
            req.start_date,
            req.end_date,
            req.ecode
        )
        return make_json_safe(data)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
