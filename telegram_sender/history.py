"""
Message history module.
Stores sent messages in JSON, supports CSV export.
"""

import json
import csv
import os
from datetime import datetime

HISTORY_FILE = "message_history.json"


def load_history() -> list:
    """Load message history from file."""
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_message(recipient: str, text: str, status: str = "sent"):
    """Save a sent message to history."""
    history = load_history()
    history.append({
        "recipient": recipient,
        "text": text,
        "status": status,
        "timestamp": datetime.now().isoformat()
    })
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def export_csv(filepath: str):
    """Export history to CSV file."""
    history = load_history()
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "recipient", "text", "status"])
        writer.writeheader()
        writer.writerows(history)


def export_json(filepath: str):
    """Export history to JSON file."""
    history = load_history()
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
