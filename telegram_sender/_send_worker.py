"""
Worker script — runs in its own process with clean event loop.
Called by telegram_client.py via subprocess.
Usage:
    python _send_worker.py --auth
    python _send_worker.py --send @username "message text"
"""

import sys
import os
import json
import asyncio
from dotenv import load_dotenv

load_dotenv()

try:
    API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
except ValueError:
    API_ID = 0
API_HASH = os.getenv("TELEGRAM_API_HASH", "")
PHONE = os.getenv("TELEGRAM_PHONE", "")
SESSION_NAME = "salon_sender"


async def auth():
    """Authenticate and create session file."""
    from telethon import TelegramClient
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.start(phone=PHONE)
    print("OK")
    await client.disconnect()


async def send(recipient: str, text: str):
    """Send message and print JSON result."""
    from telethon import TelegramClient
    from telethon.errors import (
        PhoneNumberInvalidError,
        UsernameNotOccupiedError,
        UserPrivacyRestrictedError,
        PeerFloodError,
    )

    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.connect()

    if not await client.is_user_authorized():
        print(json.dumps({"success": False, "error": "Не авторизован. Перезапустите app.py"}))
        await client.disconnect()
        return

    try:
        if recipient.startswith("@"):
            entity = await client.get_entity(recipient)
        elif recipient.startswith("+"):
            entity = await client.get_entity(recipient)
        else:
            entity = await client.get_entity("+" + recipient)

        await client.send_message(entity, text)
        print(json.dumps({"success": True, "error": None}))

    except PhoneNumberInvalidError:
        print(json.dumps({"success": False, "error": "Неверный номер телефона"}))
    except UsernameNotOccupiedError:
        print(json.dumps({"success": False, "error": "Username не найден"}))
    except UserPrivacyRestrictedError:
        print(json.dumps({"success": False, "error": "Пользователь ограничил приём сообщений"}))
    except PeerFloodError:
        print(json.dumps({"success": False, "error": "Telegram ограничил отправку (спам-лимит)"}))
    except Exception as e:
        print(json.dumps({"success": False, "error": f"Ошибка: {str(e)}"}))
    finally:
        await client.disconnect()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)

    if sys.argv[1] == "--auth":
        asyncio.run(auth())
    elif sys.argv[1] == "--send" and len(sys.argv) >= 4:
        asyncio.run(send(sys.argv[2], sys.argv[3]))
    else:
        sys.exit(1)
