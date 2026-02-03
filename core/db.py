"""
DB utilities for SmartEye Attendance Bot

Responsibilities:
- Load environment variables
- Create SQL Server connection (mill-specific)
- Fetch schema metadata
- Test database connectivity
"""

# -------------------------
# Standard imports
# -------------------------
import os
import pyodbc
from dotenv import load_dotenv

# -------------------------
# Load environment variables
# -------------------------
# Loads variables from .env file locally
# On Streamlit Cloud, secrets are injected automatically
load_dotenv()

# -------------------------
# Database credentials
# -------------------------
DB_SERVER = os.getenv("DB_SERVER")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DRIVER = os.getenv("DB_DRIVER")

# -------------------------
# Mill → Database mapping
# Ensures user cannot connect to arbitrary DBs
# -------------------------
MILL_DB_MAP = {
    "hastings": "Smart_Eye_Jute_STIL_Hastings_Live",
    "gondalpara": "Smart_Eye_Jute_STIL_Gondalpara_Live",
    "india": "Smart_Eye_Jute_STIL_India_Live",
}

# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_conn(mill: str):
    """
    Creates and returns a SQL Server connection
    for the given mill.

    Safety:
    - Only predefined mills are allowed
    """

    # Normalize input
    mill = mill.lower().strip()

    # Reject invalid mills
    if mill not in MILL_DB_MAP:
        raise ValueError(f"Invalid mill name: {mill}")

    # Build secure ODBC connection string
    conn_str = (
        f"DRIVER={{{DB_DRIVER}}};"
        f"SERVER={DB_SERVER};"
        f"DATABASE={MILL_DB_MAP[mill]};"
        f"UID={DB_USER};"
        f"PWD={DB_PASSWORD};"
        "TrustServerCertificate=yes;"
        "Connection Timeout=5;"
    )

    # Return live DB connection
    return pyodbc.connect(conn_str)

# ============================================================
# CONNECTION TESTING
# ============================================================

def test_db_connection(mill: str = "hastings"):
    """
    Tests DB connectivity using a lightweight query.
    Used during app startup to fail fast if DB is down.
    """
    conn = get_conn(mill)
    cursor = conn.cursor()

    cursor.execute("SELECT 1")  # minimal safe query
    cursor.fetchone()

    conn.close()
    return True

# ============================================================
# SCHEMA EXTRACTION (FOR LLM CONTEXT)
# ============================================================

def get_schema_text(table_names, mill: str):
    """
    Fetches column names and datatypes for given tables.

    Purpose:
    - Helps LLM understand DB structure
    - Prevents hallucinated column names
    """

    conn = get_conn(mill)
    cursor = conn.cursor()

    lines = []

    for table in table_names:
        lines.append(f"Table: {table}")
        lines.append("Columns:")

        # Query SQL Server metadata
        cursor.execute(
            """
            SELECT COLUMN_NAME, DATA_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = ?
            ORDER BY ORDINAL_POSITION
            """,
            table,
        )

        # Append each column definition
        for col, dtype in cursor.fetchall():
            lines.append(f"- {col} ({dtype})")

        lines.append("")

    conn.close()
    return "\n".join(lines)

# ============================================================
# ANALYTICS HELPERS (NO LLM USED)
# ============================================================

def get_employees_by_date_range(mill: str, start_date: str, end_date: str):
    """
    Returns list of employees who have attendance
    between given dates.
    """

    conn = get_conn(mill)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT DISTINCT
            ECode,
            EName
        FROM AttendanceReport
        WHERE WDate BETWEEN ? AND ?
        ORDER BY EName
        """,
        start_date,
        end_date,
    )

    rows = cursor.fetchall()
    conn.close()

    # Convert DB rows to clean dictionaries
    return [
        {"ECode": row[0], "EName": row[1]}
        for row in rows
    ]

def get_monthwise_attendance(mill: str, start_date: str, end_date: str, ecode: str):
    """
    Calculates:
    - Total working days per month
    - Actual attendance days for an employee
    """

    conn = get_conn(mill)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            A.mon,
            A.work_days,
            B.attn_days
        FROM
        (
            -- Total working days in mill
            SELECT
                MONTH(WDate) AS mon,
                COUNT(DISTINCT WDate) AS work_days
            FROM AttendanceReport
            WHERE WDate BETWEEN ? AND ?
            GROUP BY MONTH(WDate)
            HAVING SUM(DUTY) > 0
        ) A
        JOIN
        (
            -- Employee attendance days
            SELECT
                MONTH(WDate) AS mon,
                COUNT(DISTINCT WDate) AS attn_days
            FROM AttendanceReport
            WHERE WDate BETWEEN ? AND ?
              AND ECode = ?
            GROUP BY MONTH(WDate)
            HAVING SUM(DUTY) > 0
        ) B
        ON A.mon = B.mon
        ORDER BY A.mon
        """,
        start_date,
        end_date,
        start_date,
        end_date,
        ecode,
    )

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "mon": row[0],
            "work_days": row[1],
            "attn_days": row[2],
        }
        for row in rows
    ]
