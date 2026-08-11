"""
database.py
------------
SQLite persistence layer for the NeoFit AI Nutrition Buddy app.

Handles all reads/writes for:
    - users            (login credentials)
    - profiles         (physical stats, goals, macro targets)
    - meals            (logged meal history)

All functions open a short-lived connection per call, which is simple and
safe enough for a single-user local prototype / small multi-user demo.
"""

import sqlite3
import hashlib
import os
import secrets
from datetime import datetime, date
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "neofit.db")


# --------------------------------------------------------------------------- #
# Connection helpers
# --------------------------------------------------------------------------- #
@contextmanager
def get_conn():
    """Context-managed SQLite connection with row-factory set to dict-like rows."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """Create all tables if they do not already exist. Safe to call on every app start."""
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                identifier      TEXT UNIQUE NOT NULL,
                auth_type       TEXT NOT NULL CHECK(auth_type IN ('email', 'phone')),
                password_hash   TEXT NOT NULL,
                salt            TEXT NOT NULL,
                created_at      TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                user_id             INTEGER PRIMARY KEY,
                age                 INTEGER,
                gender              TEXT,
                weight_kg           REAL,
                height_cm           REAL,
                activity_level      TEXT,
                goal                TEXT,
                unit_pref           TEXT DEFAULT 'metric',
                calorie_target      INTEGER,
                protein_target      INTEGER,
                carb_target         INTEGER,
                fat_target          INTEGER,
                custom_override     INTEGER DEFAULT 0,
                onboarding_complete INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS meals (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id         INTEGER NOT NULL,
                log_date        TEXT NOT NULL,
                log_time        TEXT NOT NULL,
                meal_type       TEXT NOT NULL,
                description     TEXT,
                image_path      TEXT,
                calories        REAL DEFAULT 0,
                protein         REAL DEFAULT 0,
                carbs           REAL DEFAULT 0,
                fats            REAL DEFAULT 0,
                ai_feedback     TEXT,
                source          TEXT,
                created_at      TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)


# --------------------------------------------------------------------------- #
# Password hashing (PBKDF2 - stdlib only, no extra dependency required)
# --------------------------------------------------------------------------- #
def _hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000).hex()


def make_credentials(password: str):
    """Return (password_hash, salt) for a brand-new password."""
    salt = secrets.token_hex(16)
    return _hash_password(password, salt), salt


def verify_password(password: str, salt: str, password_hash: str) -> bool:
    return secrets.compare_digest(_hash_password(password, salt), password_hash)


# --------------------------------------------------------------------------- #
# User CRUD
# --------------------------------------------------------------------------- #
def create_user(identifier: str, auth_type: str, password: str):
    """Create a new user account. Returns the new user_id, or None if identifier taken."""
    password_hash, salt = make_credentials(password)
    try:
        with get_conn() as conn:
            cur = conn.execute(
                "INSERT INTO users (identifier, auth_type, password_hash, salt, created_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (identifier, auth_type, password_hash, salt, datetime.now().isoformat()),
            )
            user_id = cur.lastrowid
            conn.execute(
                "INSERT INTO profiles (user_id, onboarding_complete) VALUES (?, 0)", (user_id,)
            )
            return user_id
    except sqlite3.IntegrityError:
        return None


def get_user_by_identifier(identifier: str):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE identifier = ?", (identifier,)).fetchone()
        return dict(row) if row else None


def authenticate(identifier: str, password: str):
    """Return user dict if credentials are valid, else None."""
    user = get_user_by_identifier(identifier)
    if user and verify_password(password, user["salt"], user["password_hash"]):
        return user
    return None


def update_identifier(user_id: int, new_identifier: str) -> bool:
    try:
        with get_conn() as conn:
            conn.execute("UPDATE users SET identifier = ? WHERE id = ?", (new_identifier, user_id))
        return True
    except sqlite3.IntegrityError:
        return False


def update_password(user_id: int, new_password: str):
    password_hash, salt = make_credentials(new_password)
    with get_conn() as conn:
        conn.execute(
            "UPDATE users SET password_hash = ?, salt = ? WHERE id = ?",
            (password_hash, salt, user_id),
        )


# --------------------------------------------------------------------------- #
# Profile CRUD
# --------------------------------------------------------------------------- #
def get_profile(user_id: int):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,)).fetchone()
        return dict(row) if row else None


def save_profile(user_id: int, **fields):
    """
    Update arbitrary profile columns for a user. Only known columns are written.
    Example: save_profile(user_id, age=28, weight_kg=75.5, goal='Muscle Building')
    """
    allowed = {
        "age", "gender", "weight_kg", "height_cm", "activity_level", "goal",
        "unit_pref", "calorie_target", "protein_target", "carb_target",
        "fat_target", "custom_override", "onboarding_complete",
    }
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        return
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [user_id]
    with get_conn() as conn:
        conn.execute(f"UPDATE profiles SET {set_clause} WHERE user_id = ?", values)


# --------------------------------------------------------------------------- #
# Meal CRUD
# --------------------------------------------------------------------------- #
def log_meal(user_id: int, log_date: str, log_time: str, meal_type: str, description: str,
             calories: float, protein: float, carbs: float, fats: float,
             image_path: str = None, ai_feedback: str = None, source: str = "text"):
    with get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO meals
               (user_id, log_date, log_time, meal_type, description, image_path,
                calories, protein, carbs, fats, ai_feedback, source, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, log_date, log_time, meal_type, description, image_path,
             calories, protein, carbs, fats, ai_feedback, source, datetime.now().isoformat()),
        )
        return cur.lastrowid


def get_meals_by_date(user_id: int, log_date: str):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM meals WHERE user_id = ? AND log_date = ? ORDER BY log_time",
            (user_id, log_date),
        ).fetchall()
        return [dict(r) for r in rows]


def get_meals_by_month(user_id: int, year: int, month: int):
    prefix = f"{year:04d}-{month:02d}"
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM meals WHERE user_id = ? AND log_date LIKE ? ORDER BY log_date, log_time",
            (user_id, f"{prefix}%"),
        ).fetchall()
        return [dict(r) for r in rows]


def delete_meal(meal_id: int, user_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM meals WHERE id = ? AND user_id = ?", (meal_id, user_id))


def get_daily_totals(user_id: int, log_date: str):
    """Aggregate calories/protein/carbs/fats already logged for a given date."""
    meals = get_meals_by_date(user_id, log_date)
    totals = {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fats": 0.0}
    for m in meals:
        totals["calories"] += m["calories"] or 0
        totals["protein"] += m["protein"] or 0
        totals["carbs"] += m["carbs"] or 0
        totals["fats"] += m["fats"] or 0
    return totals


def get_logged_meal_types(user_id: int, log_date: str):
    return {m["meal_type"] for m in get_meals_by_date(user_id, log_date)}
