"""
Query runner with full safety pipeline.

Flow:
User Question
 → LLM generates SQL (JSON)
 → JSON structure validation
 → SQL safety guard (READ-ONLY)
 → Database execution

Also returns:
- Generated SQL (even if blocked)
- Parameters
- Execution confirmation

Purpose:
- Safe execution
- Debug visibility
- UI-friendly structured responses
"""

# -------------------------
# External & internal imports
# -------------------------

import pandas as pd  # Used to read SQL results into DataFrame

# Database utilities
from core.db import get_conn, get_schema_text

# SQL safety firewall
from core.sql_guard import validate_sql

# LLM interface
from core.llm_engine import generate_sql_from_question

# LLM output validator
from core.validators import validate_llm_json

# Central logging utility
from core.logger import log_event


# ============================================================
# MAIN ENTRY POINT
# ============================================================

def make_json_safe(obj):
    """
    Recursively convert numpy / pandas types
    into native Python JSON-safe types.
    """
    if isinstance(obj, dict):
        return {k: make_json_safe(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_safe(v) for v in obj]
    elif hasattr(obj, "item"):  # numpy scalar
        return obj.item()
    else:
        return obj


def handle_question(question: str, mill: str = "hastings"):
    """
    Handles a user question end-to-end in a SAFE manner.

    Parameters:
    - question : Natural language user question
    - mill     : Target mill database (default = hastings)

    Possible outcomes:

    1️⃣ EXECUTED (Safe & successful)
    {
        "status": "executed",
        "sql": "...",
        "params": [...],
        "rows": int,
        "data": DataFrame
    }

    2️⃣ GENERATED BUT BLOCKED (Unsafe SQL)
    {
        "status": "generated",
        "sql": "...",
        "params": [...],
        "message": "SQL was generated but execution was blocked"
    }

    3️⃣ UNSUPPORTED (LLM couldn't understand)
    {
        "unsupported": True,
        "message": "Query could not be understood."
    }
    """

    try:
        # ====================================================
        # STEP 1️⃣ : Fetch DB schema for LLM context
        # ====================================================
        # This prevents hallucinated columns/tables
        schema_text = get_schema_text(
            ["AttendanceReport"],  # Allowed table(s)
            mill
        )

        # ====================================================
        # STEP 2️⃣ : Convert question → SQL using LLM
        # ====================================================
        llm_result = generate_sql_from_question(
            question,
            schema_text
        )

        # ----------------------------------------------------
        # SAFETY CHECK: LLM must return a dictionary (JSON)
        # ----------------------------------------------------
        if not isinstance(llm_result, dict):
            # Log unexpected LLM output
            log_event(
                "llm_unstructured_output",
                {
                    "question": question,
                    "mill": mill,
                    "llm_result": str(llm_result)
                }
            )

            # Graceful failure (no crash)
            return {
                "unsupported": True,
                "message": "Query could not be understood."
            }

        # Extract SQL and parameters from LLM output
        sql = llm_result.get("sql")
        params = llm_result.get("params", [])

        # ====================================================
        # STEP 3️⃣ : Validate LLM JSON contract
        # ====================================================
        # Ensures:
        # - SQL exists
        # - Params are list
        # - Unsupported queries are flagged
        mode = validate_llm_json(llm_result)

        # ----------------------------------------------------
        # CASE: SQL was generated BUT execution is blocked
        # ----------------------------------------------------
        if mode == "unsupported" and sql:
            log_event(
                "sql_generated_but_blocked",
                {
                    "question": question,
                    "mill": mill,
                    "sql": sql,
                    "params": params
                }
            )

            return {
                "status": "generated",
                "sql": sql,
                "params": params,
                "message": (
                    "SQL was generated but execution was blocked "
                    "by safety rules."
                )
            }

        # ----------------------------------------------------
        # CASE: Fully unsupported (no SQL at all)
        # ----------------------------------------------------
        if mode == "unsupported":
            return {
                "unsupported": True,
                "message": "This query is not supported yet."
            }

        # ====================================================
        # STEP 4️⃣ : SQL SAFETY GUARD
        # ====================================================
        # Enforces:
        # - SELECT only
        # - No DML/DDL
        # - No forbidden tables
        validate_sql(sql)

        # ====================================================
        # STEP 5️⃣ : Execute SQL on database
        # ====================================================
        log_event(
            "sql_execution_started",
            {
                "question": question,
                "mill": mill,
                "sql": sql,
                "params": params
            }
        )

        # Open DB connection
        conn = get_conn(mill)

        # Execute query safely using parameterized SQL
        df = pd.read_sql(sql, conn, params=params)

        # Close DB connection immediately
        conn.close()

        # ====================================================
        # STEP 6️⃣ : Log successful execution
        # ====================================================
        log_event(
            "sql_executed",
            {
                "question": question,
                "mill": mill,
                "sql": sql,
                "params": params,
                "rows_returned": len(df)
            }
        )

        # Return successful response
        # return {
        #     "status": "executed",
        #     "sql": sql,
        #     "params": params,
        #     "rows": len(df),
        #     "data": df
        # }
        data = df.to_dict(orient="records")
        data = make_json_safe(data)

        return {
            "status": "executed",
            "sql": sql,
            "params": params,
            "rows": int(len(df)),
            "data": data
        }



    except Exception as e:
        # ====================================================
        # FINAL FAIL-SAFE (UI MUST NEVER CRASH)
        # ====================================================
        log_event(
            "sql_execution_error",
            {
                "question": question,
                "mill": mill,
                "error": str(e)
            }
        )

        return {
            "unsupported": True,
            "message": (
                "Query execution failed. "
                "Please refine the question."
            )
        }
