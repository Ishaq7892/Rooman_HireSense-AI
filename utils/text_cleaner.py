"""
text_cleaner.py

Cleans extracted resume and job description text.
"""

import re


def clean_text(text: str) -> str:
    """
    Clean extracted text for NLP processing.

    Args:
        text (str): Raw extracted text.

    Returns:
        str: Cleaned text.
    """

    if not text:
        return ""

    # Convert to lowercase
    text = text.lower()

    # Remove URLs
    text = re.sub(r"http\S+|www\S+", " ", text)

    # Remove email addresses
    text = re.sub(r"\S+@\S+", " ", text)

    # Remove phone numbers
    text = re.sub(r"\+?\d[\d\s()-]{8,}", " ", text)

    # Keep only letters, numbers, spaces
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()