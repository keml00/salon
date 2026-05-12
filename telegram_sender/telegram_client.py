"""
Telegram client module.
Uses subprocess to send messages — avoids all asyncio/event loop conflicts.
Each send spawns a separate Python process with its own event loop.
"""

import os
import subprocess
import sys
import json
from dotenv import load_dotenv

load_dotenv()

try:
    API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
except ValueError:
    API_ID = 0
API_HASH = os.getenv("TELEGRAM_API_HASH", "")
PHONE = os.getenv("TELEGRAM_PHONE", "")

SESSION_NAME = "salon_sender"

# Path to the send script
_SEND_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_send_worker.py")


def init_client():
    """Initialize client — run auth script to create/verify session."""
    result = subprocess.run(
        [sys.executable, _SEND_SCRIPT, "--auth"],
        capture_output=True, text=True, timeout=120,
        # Pass through stdin for code input
        stdin=sys.stdin
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Auth failed")


def send_message(recipient: str, text: str) -> dict:
    """
    Send message via subprocess (no event loop issues).
    Returns: {"success": bool, "error": str|None}
    """
    if not text.strip():
        return {"success": False, "error": "Сообщение пустое"}
    if not recipient.strip():
        return {"success": False, "error": "Получатель не указан"}

    try:
        result = subprocess.run(
            [sys.executable, _SEND_SCRIPT, "--send", recipient, text],
            capture_output=True, text=True, timeout=30
        )
        data = json.loads(result.stdout)
        return data
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Таймаут отправки (30 сек)"}
    except (json.JSONDecodeError, Exception) as e:
        stderr = result.stderr.strip() if 'result' in dir() else str(e)
        return {"success": False, "error": f"Ошибка: {stderr or str(e)}"}


def disconnect():
    """No-op for subprocess approach."""
    pass
