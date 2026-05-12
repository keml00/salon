"""
Telegram client module.
Uses Telethon to send messages by phone number or username.
Runs Telethon in its own dedicated thread with its own event loop.
"""

import os
import asyncio
import threading
from telethon.sync import TelegramClient
from telethon.errors import (
    PhoneNumberInvalidError,
    UsernameNotOccupiedError,
    UserPrivacyRestrictedError,
    PeerFloodError,
)
from dotenv import load_dotenv

load_dotenv()

try:
    API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
except ValueError:
    API_ID = 0
API_HASH = os.getenv("TELEGRAM_API_HASH", "")
PHONE = os.getenv("TELEGRAM_PHONE", "")

SESSION_NAME = "salon_sender"

# Global sync client (telethon.sync wraps async automatically)
_client = None
_lock = threading.Lock()


def init_client():
    """Initialize and connect client (blocks, asks for code in terminal)."""
    global _client
    _client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    _client.start(phone=PHONE)
    print("  Telegram session ready.")


def send_message(recipient: str, text: str) -> dict:
    """
    Send message to recipient (synchronous).
    recipient: phone number (+7...) or @username
    Returns: {"success": bool, "error": str|None}
    """
    if not text.strip():
        return {"success": False, "error": "Сообщение пустое"}
    if not recipient.strip():
        return {"success": False, "error": "Получатель не указан"}

    with _lock:
        try:
            if recipient.startswith("@"):
                entity = _client.get_entity(recipient)
            elif recipient.startswith("+"):
                entity = _client.get_entity(recipient)
            else:
                entity = _client.get_entity("+" + recipient)

            _client.send_message(entity, text)
            return {"success": True, "error": None}

        except PhoneNumberInvalidError:
            return {"success": False, "error": "Неверный номер телефона"}
        except UsernameNotOccupiedError:
            return {"success": False, "error": "Username не найден"}
        except UserPrivacyRestrictedError:
            return {"success": False, "error": "Пользователь ограничил приём сообщений"}
        except PeerFloodError:
            return {"success": False, "error": "Telegram ограничил отправку (спам-лимит)"}
        except Exception as e:
            return {"success": False, "error": f"Ошибка: {str(e)}"}


def disconnect():
    """Disconnect client."""
    global _client
    if _client:
        _client.disconnect()
        _client = None
