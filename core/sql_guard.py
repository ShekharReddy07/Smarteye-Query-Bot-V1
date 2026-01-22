"""
SQL Guard
Ensures only safe, read-only SQL queries are executed
"""

import re

# Block all dangerous SQL operations
FORBIDDEN_KEYWORDS = [
    "insert", "update", "delete", "drop",
    "alter", "create", "merge", "exec",
    "truncate", "grant", "revoke"
]

# Only this table is allowed
ALLOWED_TABLES = {"attendancereport"}

def validate_sql(sql: str):
    """
    Validates SQL query for safety.
    Raises ValueError if unsafe.
    """

    if not sql:
        raise ValueError("Empty SQL")

    sql_clean = sql.strip().lower()

    # 1️⃣ Must start with SELECT
    if not sql_clean.startswith("select"):
        raise ValueError("Only SELECT queries are allowed")

    # 2️⃣ No semicolons (prevents multi-statement)
    if ";" in sql_clean:
        raise ValueError("Semicolons are not allowed")

    # 3️⃣ Block forbidden keywords
    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{keyword}\b", sql_clean):
            raise ValueError(f"Forbidden SQL keyword detected: {keyword}")

    # 4️⃣ Enforce allowed table(s)
    tables = re.findall(r"from\s+([a-zA-Z0-9_]+)", sql_clean)
    for table in tables:
        if table not in ALLOWED_TABLES:
            raise ValueError(f"Access to table '{table}' is not allowed")

    return True
