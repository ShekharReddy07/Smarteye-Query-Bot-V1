"""
Validators
Ensures LLM output strictly follows expected JSON format
"""

def validate_llm_json(obj: dict):
    """
    Validates LLM output structure.

    Returns:
    - "sql" if executable
    - "unsupported" if blocked
    """

    if not isinstance(obj, dict):
        raise ValueError("LLM output is not a JSON object")

    # Unsupported path
    if obj.get("unsupported") is True:
        if "message" not in obj:
            raise ValueError("Unsupported JSON missing message")
        return "unsupported"

    # SQL path
    if "sql" not in obj:
        raise ValueError("LLM JSON missing 'sql' key")

    sql = obj.get("sql")
    params = obj.get("params", [])

    if not isinstance(sql, str) or not sql.strip():
        raise ValueError("SQL is empty or invalid")

    if not isinstance(params, list):
        raise ValueError("'params' must be a list")

    return "sql"
