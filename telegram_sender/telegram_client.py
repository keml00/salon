"""
Telegram client module.
Uses Telethon to send messages by phone number or username.
Single persistent event loop approach.
"""

import os
import asyncio
import threading
from telethon import TelegramClient
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

# Persistent event loop running in background thread
_loop = asyncio.new_event_loop()
_thread = threading.Thread(target=_loop.run_forever, daemon=True)
_thread.start()

# Global client — created and used ONLY in _loop
_client = None


async def _get_client():
    """Get or create Telegram client (runs in _loop)."""
    global _client
    if _client is None:
        _client = TelegramClient(SESSION_NAME, API_ID, API_HASH, loop=_loop)
        await _client.start(phone=PHONE)
    elif not _client.is_connected():
        await _client.connect()
    return _client


def init_client():
    """Initialize client (call from main thread, blocks until done)."""
    future = asyncio.run_coroutine_threadsafe(_get_client(), _loop)
    return future.result(timeout=60)


async def _send(recipient: str, text: str) -> dict:
    """Internal send (runs in _loop)."""
    if not text.strip():
        return {"success": False, "error": "Сообщение пустое"}
    if not recipient.strip():
        return {"success": False, "error": "Получатель не указан"}

    try:
        client = await _get_client()

        if recipient.startswith("@"):
            entity = await client.get_entity(recipient)
        elif recipient.startswith("+"):
            entity = await client.get_entity(recipient)
        else:
            entity = await client.get_entity("+" + recipient)

        await client.send_message(entity, text)
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


def send_message(recipient: str, text: str) -> dict:
    """Send message (call from any thread, synchronous)."""
    future = asyncio.run_coroutine_threadsafe(_send(recipient, text), _loop)
    return future.result(timeout=30)


def disconnect():
    """Disconnect client."""
    global _client
    if _client:
        asyncio.run_coroutine_threadsafe(_client.disconnect(), _loop).result(timeout=10)
        _client = None
