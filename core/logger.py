"""
Central Logger
Purpose:
- Track LLM requests
- Track SQL execution
- Provide audit trail for debugging & compliance
"""

import datetime
import json
from pathlib import Path

# Create logs directory if missing
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

def log_event(event_type: str, payload: dict):
    """
    Writes a structured JSON log entry
    into a daily log file.
    """

    # One log file per day
    log_file = LOG_DIR / f"{datetime.date.today()}.log"

    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "event": event_type,
        "payload": payload
    }

    # Append log entry
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

    # Print for live debugging
    print(entry)
