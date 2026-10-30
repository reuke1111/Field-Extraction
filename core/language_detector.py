"""
Language detector for scheme documents.
Uses deterministic Unicode script range analysis to classify text into 'en', 'hi', or 'mixed'.
Zero external model dependencies for maximum reliability.
"""

import re
from typing import Literal

DEVANAGARI_REGEX = re.compile(r'[\u0900-\u097F]')
LATIN_REGEX = re.compile(r'[a-zA-Z]')

def detect_language(text: str) -> Literal["en", "hi", "mixed"]:
    """
    Analyzes character distribution across Devanagari and Latin Unicode ranges.
    Returns: 'en', 'hi', or 'mixed'
    """
    if not text or not text.strip():
        return "en"

    devanagari_count = len(DEVANAGARI_REGEX.findall(text))
    latin_count = len(LATIN_REGEX.findall(text))
    total_letters = devanagari_count + latin_count

    if total_letters == 0:
        return "en"

    devanagari_ratio = devanagari_count / total_letters

    if devanagari_ratio > 0.40:
        if latin_count > 0.30 * total_letters:
            return "mixed"
        return "hi"
    elif devanagari_ratio > 0.05:
        return "mixed"
    else:
        return "en"
