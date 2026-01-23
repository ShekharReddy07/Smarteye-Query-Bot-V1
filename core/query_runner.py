"""
Query runner with full safety:
LLM → JSON validation → SQL guard → DB

Also returns:
- Generated SQL (even if blocked)
- Parameters
- Execution confirmation
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

    Possible outcomes:

    EXECUTED:
    {
        "status": "executed",
        "sql": "...",
        "params": [...],
        "rows": int,
        "data": DataFrame
    }

    GENERATED BUT BLOCKED:
    {
        "status": "generated",
        "sql": "...",
        "params": [...],
        "message": "SQL was generated but execution was blocked"
    }

    UNSUPPORTED:
    {
        "unsupported": True,
        "message": "Query could not be understood."
    }
    """

    try:
        # 1️⃣ Fetch schema for LLM
        schema_text = get_schema_text(["AttendanceReport"], mill)

        # 2️⃣ LLM → SQL generation
        llm_result = generate_sql_from_question(question, schema_text)

        # 🔴 LLM failed to produce structured output
        if not isinstance(llm_result, dict):
            log_event("llm_unstructured_output", {
                "question": question,
                "mill": mill,
                "llm_result": str(llm_result)
            })
            return {
                "unsupported": True,
                "message": "Query could not be understood."
            }

        sql = llm_result.get("sql")
        params = llm_result.get("params", [])

        # 3️⃣ Validate LLM JSON contract
        mode = validate_llm_json(llm_result)

        # 🟡 SQL GENERATED BUT BLOCKED (DO NOT EXECUTE)
        if mode == "unsupported" and sql:
            log_event("sql_generated_but_blocked", {
                "question": question,
                "mill": mill,
                "sql": sql,
                "params": params
            })

            return {
                "status": "generated",
                "sql": sql,
                "params": params,
                "message": "SQL was generated but execution was blocked by safety rules."
            }

        # 🔴 Fully unsupported (no SQL)
        if mode == "unsupported":
            return {
                "unsupported": True,
                "message": "This query is not supported yet."
            }

        # 4️⃣ SQL safety guard (READ-ONLY enforcement)
        validate_sql(sql)

        # 5️⃣ Execute SQL on database
        log_event("sql_execution_started", {
            "question": question,
            "mill": mill,
            "sql": sql,
            "params": params
        })

        conn = get_conn(mill)
        df = pd.read_sql(sql, conn, params=params)
        conn.close()

        # 6️⃣ Confirm execution
        log_event("sql_executed", {
            "question": question,
            "mill": mill,
            "sql": sql,
            "params": params,
            "rows_returned": len(df)
        })

        return {
            "status": "executed",
            "sql": sql,
            "params": params,
            "rows": len(df),
            "data": df
        }

    except Exception as e:
        # ❗ Hard fallback – never crash UI
        log_event("sql_execution_error", {
            "question": question,
            "mill": mill,
            "error": str(e)
        })

        return {
            "unsupported": True,
            "message": "Query execution failed. Please refine the question."
        }
