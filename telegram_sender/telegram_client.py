"""
Telegram client module.
Uses Telethon to send messages by phone number or username.
"""

import os
import asyncio
from telethon import TelegramClient
from telethon.errors import (
    PhoneNumberInvalidError,
    UsernameNotOccupiedError,
    UserPrivacyRestrictedError,
    PeerFloodError,
)
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
API_HASH = os.getenv("TELEGRAM_API_HASH", "")
PHONE = os.getenv("TELEGRAM_PHONE", "")

SESSION_NAME = "salon_sender"

# Global client instance
_client = None


async def get_client():
    """Get or create Telegram client."""
    global _client
    if _client is None or not _client.is_connected():
        _client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
        await _client.start(phone=PHONE)
    return _client


async def send_message(recipient: str, text: str) -> dict:
    """
    Send message to recipient.
    recipient: phone number (+7...) or @username
    Returns: {"success": bool, "error": str|None}
    """
    if not text.strip():
        return {"success": False, "error": "Сообщение пустое"}

    if not recipient.strip():
        return {"success": False, "error": "Получатель не указан"}

    try:
        client = await get_client()

        # Resolve recipient
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


async def disconnect():
    """Disconnect client."""
    global _client
    if _client and _client.is_connected():
        await _client.disconnect()
        _client = None
