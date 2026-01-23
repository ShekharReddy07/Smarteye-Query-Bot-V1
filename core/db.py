"""
DB utilities for SmartEye Attendance Bot

Responsibilities:
- Load environment variables
- Create SQL Server connection (mill-specific)
- Fetch schema metadata
- Provide simple test connectivity

NOTE:
- Uses pymssql (pure Python, works on Streamlit Cloud & Linux)
- Avoids pyodbc / unixODBC dependency issues
"""

import os
import pymssql
from dotenv import load_dotenv

# Load environment variables (.env locally, Streamlit secrets in cloud)
load_dotenv()

DB_SERVER = os.getenv("DB_SERVER")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Mill → Database mapping
MILL_DB_MAP = {
    "hastings": "Smart_Eye_Jute_STIL_Hastings_Live",
    "gondalpara": "Smart_Eye_Jute_STIL_Gondalpara_Live",
    "india": "Smart_Eye_Jute_STIL_India_Live",
}


def get_conn(mill: str):
    """
    Create and return a SQL Server connection for a given mill.

    Raises:
        ValueError: if mill name is invalid
        pymssql.Error: if DB connection fails
    """
    mill = mill.lower().strip()

    if mill not in MILL_DB_MAP:
        raise ValueError(f"Invalid mill name: {mill}")

    return pymssql.connect(
        server=DB_SERVER,
        user=DB_USER,
        password=DB_PASSWORD,
        database=MILL_DB_MAP[mill],
        login_timeout=5,
        timeout=10,
    )


def test_db_connection(mill: str = "hastings"):
    """
    Tests database connectivity by executing a lightweight query.

    Returns:
        True if connection and query succeed
    """
    conn = get_conn(mill)
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    cursor.fetchone()
    conn.close()
    return True


def get_schema_text(table_names, mill: str):
    """
    Fetch schema (column names + datatypes) for given tables.
    Used by LLM to understand DB structure.

    Args:
        table_names (list[str]): list of table names
        mill (str): mill identifier

    Returns:
        str: formatted schema text
    """
    conn = get_conn(mill)
    cursor = conn.cursor()

    lines = []

    for table in table_names:
        lines.append(f"Table: {table}")
        lines.append("Columns:")

        cursor.execute(
            """
            SELECT COLUMN_NAME, DATA_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = %s
            ORDER BY ORDINAL_POSITION
            """,
            (table,),
        )

        for col, dtype in cursor.fetchall():
            lines.append(f"- {col} ({dtype})")

        lines.append("")

    conn.close()
    return "\n".join(lines)
