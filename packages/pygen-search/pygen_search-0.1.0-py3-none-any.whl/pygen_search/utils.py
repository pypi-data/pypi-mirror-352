# pygen_search/utils.py

import re

def clean_text(text: str) -> str:
    """Lowercase and remove special characters for uniformity."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text

def tokenize(text: str) -> list:
    """Break text into tokens (words)."""
    text = clean_text(text)
    return text.split()

def join_tokens(tokens: list) -> str:
    """Rejoin tokens to a string (if needed)."""
    return " ".join(tokens)
