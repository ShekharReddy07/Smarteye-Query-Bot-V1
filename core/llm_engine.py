"""
LLM Engine
Converts user question into SQL JSON
"""

import os
import json
from pathlib import Path
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def load_llm_files():
    """
    Loads instruction, rules, and examples for prompt
    """
    base = Path(__file__).resolve().parent.parent / "llm"

    return {
        "instructions": (base / "instructions.md").read_text(encoding="utf-8"),
        "rules": (base / "sql_rules.md").read_text(encoding="utf-8"),
        "examples": (base / "examples.md").read_text(encoding="utf-8"),
    }

def generate_sql_from_question(question: str, schema_text: str):
    """
    Sends prompt to LLM and returns parsed JSON
    """

    files = load_llm_files()

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

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You generate SQL only."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    raw = response.choices[0].message.content.strip()

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError(f"LLM returned invalid JSON: {raw}")

    return parsed

