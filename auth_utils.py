"""
auth_utils.py
-------------
Lightweight validation and normalization helpers for email/phone auth.
"""

import re

EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
PHONE_RE = re.compile(r"^\+?[0-9]{7,15}$")


def detect_identifier_type(identifier: str):
    """Return 'email', 'phone', or None if the identifier matches neither format."""
    if not identifier:
        return None
    cleaned = identifier.strip()
    if EMAIL_RE.match(cleaned):
        return "email"
    phone_digits = cleaned.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if PHONE_RE.match(phone_digits):
        return "phone"
    return None


def normalize_identifier(identifier: str) -> str:
    """Normalize identifiers so login credentials match consistently regardless of phone formatting or case."""
    if not identifier:
        return ""
    cleaned = identifier.strip()
    auth_type = detect_identifier_type(cleaned)
    if auth_type == "email":
        return cleaned.lower()
    elif auth_type == "phone":
        return cleaned.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    return cleaned


def is_valid_password(password: str) -> bool:
    """Minimum viable password policy for the prototype: at least 6 characters."""
    return bool(password) and len(password) >= 6
