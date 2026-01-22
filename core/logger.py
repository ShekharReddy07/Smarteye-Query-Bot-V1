"""
Central logger for SmartEye Attendance Bot
Logs LLM inputs, outputs, and execution status
"""

import datetime
import json
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

def log_event(event_type: str, payload: dict):
    """
    Appends structured logs to a daily log file
    """
    log_file = LOG_DIR / f"{datetime.date.today()}.log"

    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "event": event_type,
        "payload": payload
    }

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
