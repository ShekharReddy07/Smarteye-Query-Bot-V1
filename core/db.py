"""
DB utilities for SmartEye Attendance Bot

Responsibilities:
- Load environment variables
- Create SQL Server connection
- Simple test query execution
"""

import os
import pyodbc
from dotenv import load_dotenv

# Load .env file
load_dotenv()

DB_SERVER = os.getenv("DB_SERVER")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DRIVER = os.getenv("DB_DRIVER")

# Mill → Database mapping
MILL_DB_MAP = {
    "hastings": "Smart_Eye_Jute_STIL_Hastings_Live",
    "gondalpara": "Smart_Eye_Jute_STIL_Gondalpara_Live",
    "india": "Smart_Eye_Jute_STIL_India_Live",
}

def get_conn(mill: str):
    """
    Returns an active DB connection for a given mill
    """
    mill = mill.lower()

    if mill not in MILL_DB_MAP:
        raise ValueError("Invalid mill name")

    conn_str = (
        f"DRIVER={{{DB_DRIVER}}};"
        f"SERVER={DB_SERVER};"
        f"DATABASE={MILL_DB_MAP[mill]};"
        f"UID={DB_USER};"
        f"PWD={DB_PASSWORD}"
    )

    return pyodbc.connect(conn_str)

def test_db_connection(mill="hastings"):
    """
    Runs a simple test query
    """
    conn = get_conn(mill)
    cursor = conn.cursor()
    cursor.execute("SELECT TOP 5 * FROM AttendanceReport")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_schema_text(table_names, mill):
    """
    Fetch schema of given tables for the selected mill
    Used by LLM to understand DB structure
    """
    conn = get_conn(mill)
    cursor = conn.cursor()

    lines = []

    for table in table_names:
        lines.append(f"Table: {table}")
        lines.append("Columns:")

        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = ?
            ORDER BY ORDINAL_POSITION
        """, table)

        for col, dtype in cursor.fetchall():
            lines.append(f"- {col} ({dtype})")

        lines.append("")

    conn.close()
    return "\n".join(lines)

