-- =============================================================================
-- AirVision AI — SQLite Schema
-- =============================================================================

-- Generic key/value cache used to persist API responses across restarts so
-- the dashboard can always show the last successful data even when the
-- upstream API is temporarily unavailable.
CREATE TABLE IF NOT EXISTS cache (
    key         TEXT PRIMARY KEY,          -- e.g. "live:air_quality"
    payload     TEXT NOT NULL,             -- JSON-encoded response
    created_at  REAL NOT NULL,             -- epoch seconds when stored
    expires_at  REAL NOT NULL             -- epoch seconds when stale
);

-- Audit log of outbound OpenWeather API calls (helps track rate-limit usage).
CREATE TABLE IF NOT EXISTS api_log (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    endpoint   TEXT NOT NULL,              -- e.g. "air_pollution"
    city       TEXT,
    status     INTEGER NOT NULL,           -- HTTP status of the upstream call
    took_ms    INTEGER,
    ts         REAL NOT NULL
);

-- Persistent store of the last successful city payloads (fallback source of
-- truth when the live API is unreachable).
CREATE TABLE IF NOT EXISTS city_snapshot (
    city_id     TEXT PRIMARY KEY,          -- e.g. "delhi"
    payload     TEXT NOT NULL,             -- JSON city record
    updated_at  REAL NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_api_log_ts ON api_log (ts);
