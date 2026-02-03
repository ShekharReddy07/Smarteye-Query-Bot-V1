"""
LLM Engine
Purpose:
- Converts natural language questions into SQL JSON
- Uses strict instructions + schema + examples
"""

import os
import json
from pathlib import Path
from openai import OpenAI

# Initialize OpenAI client using API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ============================================================
# LOAD PROMPT FILES
# ============================================================

def load_llm_files():
    """
    Loads:
    - Instructions
    - SQL safety rules
    - Example queries

    These guide the LLM to behave safely.
    """

    base = Path(__file__).resolve().parent.parent / "llm"

    return {
        "instructions": (base / "instructions.md").read_text(encoding="utf-8"),
        "rules": (base / "sql_rules.md").read_text(encoding="utf-8"),
        "examples": (base / "examples.md").read_text(encoding="utf-8"),
    }

# ============================================================
# GENERATE SQL FROM USER QUESTION
# ============================================================

def generate_sql_from_question(question: str, schema_text: str):
    """
    Sends structured prompt to LLM and returns parsed JSON.

    Output format enforced:
    {
        "sql": "...",
        "params": []
    }
    """

    files = load_llm_files()

    # Construct prompt with strict structure
    prompt = f"""
        {files['instructions']}

        {files['rules']}

        SCHEMA:
        {schema_text}

        EXAMPLES:
        {files['examples']}

        USER QUESTION:
        {question}

        Return ONLY valid JSON.
    """

    # Call OpenAI chat completion
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You generate SQL only."},
            {"role": "user", "content": prompt}
        ],
        temperature=0  # deterministic output
    )

    raw = response.choices[0].message.content.strip()

    # Parse JSON safely
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError(f"LLM returned invalid JSON: {raw}")

    return parsed
