"""
AI text formatter module.
Uses free LLM APIs (OpenRouter) to improve message text.
Uses urllib (built-in) — no C compilation needed on Windows.
"""

import json
import os
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from dotenv import load_dotenv

load_dotenv()

AI_API_URL = os.getenv("AI_API_URL", "https://openrouter.ai/api/v1/chat/completions")
AI_API_KEY = os.getenv("AI_API_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "meta-llama/llama-3-8b-instruct:free")

SYSTEM_PROMPT = (
    "You are a text assistant for a salon business. "
    "Improve the given message: fix grammar, make it polite, professional and concise. "
    "Keep the same language as input. Return ONLY the improved text, nothing else."
)


def format_text(text: str) -> str:
    """Send text to AI API and return formatted version."""
    if not AI_API_KEY:
        return "[ERROR] AI_API_KEY not set in .env"

    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = json.dumps({
        "model": AI_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        "max_tokens": 500,
    }).encode("utf-8")

    try:
        req = Request(AI_API_URL, data=payload, headers=headers, method="POST")
        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"].strip()
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")[:200]
        return f"[AI ERROR {e.code}] {body}"
    except URLError as e:
        return f"[AI ERROR] {str(e.reason)}"
    except Exception as e:
        return f"[AI ERROR] {str(e)}"
