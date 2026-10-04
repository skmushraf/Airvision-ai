"""
AirVision AI — SQLite Data Access Layer
=======================================
Thin wrapper around the standard-library sqlite3 module. Provides:
  - schema initialisation (from schema.sql)
  - JSON cache get/set with TTL
  - city snapshot persistence (last-successful-data fallback)
  - API call audit logging
"""

import json
import sqlite3
import threading
import time
from pathlib import Path

from config import Config

_lock = threading.Lock()
_connection = None


def _get_connection() -> sqlite3.Connection:
    """Return a thread-safe singleton connection (check_same_thread=False)."""
    global _connection
    with _lock:
        if _connection is None:
            Path(Config.DB_PATH).parent.mkdir(parents=True, exist_ok=True)
            _connection = sqlite3.connect(Config.DB_PATH, check_same_thread=False)
            _connection.row_factory = sqlite3.Row
            _connection.execute("PRAGMA journal_mode=WAL;")
            _init_schema(_connection)
        return _connection


def _init_schema(conn: sqlite3.Connection):
    """Execute the schema script."""
    schema_path = Path(__file__).parent / "schema.sql"
    conn.executescript(schema_path.read_text())
    conn.commit()


# ---------------------------------------------------------------------------
# Cache helpers
# ---------------------------------------------------------------------------
def cache_get(key: str):
    """Return cached JSON value if present and not expired, else None."""
    conn = _get_connection()
    now = time.time()
    row = conn.execute(
        "SELECT payload, expires_at FROM cache WHERE key = ?", (key,)
    ).fetchone()
    if row is None:
        return None
    if row["expires_at"] < now:
        conn.execute("DELETE FROM cache WHERE key = ?", (key,))
        conn.commit()
        return None
    return json.loads(row["payload"])


def cache_set(key: str, payload, ttl_seconds: int = None):
    """Store a JSON-serialisable value with a TTL."""
    ttl = ttl_seconds or Config.CACHE_TTL_SECONDS
    now = time.time()
    conn = _get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO cache (key, payload, created_at, expires_at) "
        "VALUES (?, ?, ?, ?)",
        (key, json.dumps(payload), now, now + ttl),
    )
    conn.commit()


def cache_clear_prefix(prefix: str):
    conn = _get_connection()
    conn.execute("DELETE FROM cache WHERE key LIKE ?", (f"{prefix}%",))
    conn.commit()


# ---------------------------------------------------------------------------
# City snapshot helpers (last-successful-data fallback)
# ---------------------------------------------------------------------------
def snapshot_get(city_id: str):
    conn = _get_connection()
    row = conn.execute(
        "SELECT payload, updated_at FROM city_snapshot WHERE city_id = ?",
        (city_id,),
    ).fetchone()
    return row


def snapshot_set(city_id: str, payload):
    conn = _get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO city_snapshot (city_id, payload, updated_at) "
        "VALUES (?, ?, ?)",
        (city_id, json.dumps(payload), time.time()),
    )
    conn.commit()


def snapshot_all() -> dict:
    """Return {city_id: payload} for every stored snapshot."""
    conn = _get_connection()
    rows = conn.execute("SELECT city_id, payload FROM city_snapshot").fetchall()
    return {row["city_id"]: json.loads(row["payload"]) for row in rows}


# ---------------------------------------------------------------------------
# API audit log
# ---------------------------------------------------------------------------
def log_api_call(endpoint: str, status: int, city: str = None, took_ms: int = None):
    try:
        conn = _get_connection()
        conn.execute(
            "INSERT INTO api_log (endpoint, city, status, took_ms, ts) "
            "VALUES (?, ?, ?, ?, ?)",
            (endpoint, city, status, took_ms, time.time()),
        )
        conn.commit()
    except Exception:
        pass  # logging must never break the request


def api_call_count_last_24h() -> int:
    conn = _get_connection()
    row = conn.execute(
        "SELECT COUNT(*) AS n FROM api_log WHERE ts > ?", (time.time() - 86400,)
    ).fetchone()
    return row["n"] if row else 0
