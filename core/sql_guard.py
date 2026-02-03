"""
SQL Guard
Ensures ONLY safe, read-only SQL runs
"""

import re

# Keywords that can modify or destroy data
FORBIDDEN_KEYWORDS = [
    "insert", "update", "delete", "drop",
    "alter", "create", "merge", "exec",
    "truncate", "grant", "revoke"
]

# Restrict access to known table only
ALLOWED_TABLES = {"attendancereport"}

def validate_sql(sql: str):
    """
    Validates SQL query for safety.
    Raises ValueError if unsafe.
    """

    if not sql:
        raise ValueError("Empty SQL")

    sql_clean = sql.strip().lower()

    # Must be SELECT
    if not sql_clean.startswith("select"):
        raise ValueError("Only SELECT queries are allowed")

    # Block multi-statement queries
    if ";" in sql_clean:
        raise ValueError("Semicolons are not allowed")

    # Block dangerous keywords
    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{keyword}\b", sql_clean):
            raise ValueError(f"Forbidden SQL keyword detected: {keyword}")

    # Enforce allowed tables only
    tables = re.findall(r"from\s+([a-zA-Z0-9_]+)", sql_clean)
    for table in tables:
        if table not in ALLOWED_TABLES:
            raise ValueError(f"Access to table '{table}' is not allowed")

    return True
