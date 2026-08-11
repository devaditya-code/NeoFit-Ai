"""
auth_utils.py
-------------
Lightweight validation helpers for the email/phone based auth system.
Password hashing itself lives in database.py (PBKDF2, stdlib only).
"""

import re

EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
PHONE_RE = re.compile(r"^\+?[0-9]{7,15}$")


def detect_identifier_type(identifier: str):
    """Return 'email', 'phone', or None if the identifier matches neither format."""
    identifier = identifier.strip()
    if EMAIL_RE.match(identifier):
        return "email"
    if PHONE_RE.match(identifier.replace(" ", "").replace("-", "")):
        return "phone"
    return None


def is_valid_password(password: str) -> bool:
    """Minimum viable password policy for the prototype: at least 6 characters."""
    return bool(password) and len(password) >= 6
