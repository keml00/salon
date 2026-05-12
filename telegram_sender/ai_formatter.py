"""
AI text formatter module.
Simple local text improvement (no external API needed).
"""

import os
from dotenv import load_dotenv

load_dotenv()


def format_text(text: str) -> str:
    """
    Improve text locally without AI API.
    Simple formatting: capitalize, trim spaces, add punctuation.
    """
    # Basic local formatting (no API needed)
    result = text.strip()
    # Capitalize first letter
    if result:
        result = result[0].upper() + result[1:]
    # Add period if no punctuation at end
    if result and result[-1] not in ".!?…":
        result += "."
    # Remove double spaces
    while "  " in result:
        result = result.replace("  ", " ")
    return result
