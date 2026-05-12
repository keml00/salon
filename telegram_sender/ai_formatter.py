"""
AI text formatter module.
Uses free LLM APIs (OpenRouter / Ollama) to improve message text.
"""

import aiohttp
import os
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


async def format_text(text: str) -> str:
    """Send text to AI API and return formatted version."""
    if not AI_API_KEY:
        return "[ERROR] AI_API_KEY not set in .env"

    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": AI_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        "max_tokens": 500,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(AI_API_URL, json=payload, headers=headers) as resp:
                if resp.status != 200:
                    error = await resp.text()
                    return f"[AI ERROR {resp.status}] {error[:200]}"
                data = await resp.json()
                return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"[AI ERROR] {str(e)}"
