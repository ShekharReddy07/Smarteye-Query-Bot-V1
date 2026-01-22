"""
Query runner with full safety:
LLM → JSON validation → SQL guard → DB

Also returns:
- Executed SQL
- Parameters
(for UI display / SSMS visibility)
"""

import pandas as pd
from core.db import get_conn, get_schema_text
from core.sql_guard import validate_sql
from core.llm_engine import generate_sql_from_question
from core.validators import validate_llm_json
from core.logger import log_event


def handle_question(question: str, mill: str = "hastings"):
    """
    Full safe pipeline.
    Never raises uncaught exceptions to UI.

    Returns on success:
    {
        "status": "ok",
        "data": DataFrame,
        "sql": "<executed sql>",
        "params": [...]
    }

    Returns on failure:
    {
        "unsupported": True,
        "message": "This query is not supported yet. We will work on that."
    }
    """

    try:
        # 1️⃣ Fetch schema for LLM
        schema_text = get_schema_text(["AttendanceReport"], mill)

        # 2️⃣ Generate SQL via LLM
        llm_result = generate_sql_from_question(question, schema_text)

        # 3️⃣ Validate LLM JSON structure
        mode = validate_llm_json(llm_result)

        # 🚫 Unsupported query (LLM decided)
        if mode == "unsupported":
            log_event("unsupported", {
                "question": question,
                "mill": mill
            })
            return llm_result

        sql = llm_result["sql"]
        params = llm_result.get("params", [])

        # 4️⃣ SQL safety guard
        validate_sql(sql)

        # 5️⃣ Execute query safely
        conn = get_conn(mill)
        df = pd.read_sql(sql, conn, params=params)
        conn.close()

        # 6️⃣ Log success
        log_event("success", {
            "question": question,
            "mill": mill,
            "sql": sql,
            "params": params,
            "rows": len(df)
        })

        # ✅ SUCCESS RETURN (UI + SSMS visibility)
        return {
            "status": "ok",
            "data": df,
            "sql": sql,
            "params": params
        }

    except Exception as e:
        # ❗ Final hard fallback – never crash UI
        log_event("error", {
            "question": question,
            "mill": mill,
            "error": str(e)
        })

        return {
            "unsupported": True,
            "message": "This query is not supported yet. We will work on that."
        }
