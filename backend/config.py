"""
AirVision AI — Backend Configuration
====================================
All configuration is read from environment variables (never hardcoded).
The .env file is loaded by python-dotenv at app startup.
"""

import os

from dotenv import load_dotenv

# Load environment variables from backend/.env (ignored by git)
load_dotenv()


class Config:
    """Central configuration object for the Flask backend."""

    # --- OpenWeather -------------------------------------------------------
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "").strip()
    OW_BASE_URL = os.getenv(
        "OW_BASE_URL", "https://api.openweathermap.org/data/2.5"
    )
    OW_GEO_URL = os.getenv(
        "OW_GEO_URL", "https://api.openweathermap.org/geo/1.0"
    )
    OW_UNITS = "metric"

    # --- CPCB / data.gov.in (PRIMARY source for Indian cities) --------------
    # Open Government Data Platform India — CPCB real-time AQI resource.
    # Key is read from the environment and never shipped to the frontend.
    DATA_GOV_API_KEY = os.getenv("DATA_GOV_API_KEY", "").strip()
    DATA_GOV_BASE_URL = os.getenv("DATA_GOV_BASE_URL", "https://api.data.gov.in")
    CPCB_RESOURCE_ID = os.getenv(
        "CPCB_RESOURCE_ID", "3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69"
    )
    # Use CPCB as the primary provider for Indian cities (1) or OpenWeather (0)
    ENABLE_CPCB = os.getenv("ENABLE_CPCB", "1") == "1"
    # The CPCB feed updates ~hourly, so cache longer than the OpenWeather TTL
    CPCB_TTL_SECONDS = int(os.getenv("CPCB_TTL_SECONDS", "900"))
    CPCB_TIMEOUT = int(os.getenv("CPCB_TIMEOUT", "20"))
    CPCB_PAGE_SIZE = int(os.getenv("CPCB_PAGE_SIZE", "1000"))
    CPCB_MAX_RECORDS = int(os.getenv("CPCB_MAX_RECORDS", "20000"))
    # CO unit handling in the feed: auto | ug | mg  (see services/cpcb.py)
    CPCB_CO_UNIT = os.getenv("CPCB_CO_UNIT", "auto").strip().lower()

    # --- Caching / refresh --------------------------------------------------
    # Data cache TTL in seconds (dashboard auto-refreshes on this cadence)
    CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "300"))
    # Whether a background thread auto-refreshes all cities every TTL.
    # Disabled by default to respect free-tier API limits (1,000 calls/day).
    ENABLE_AUTO_REFRESH = os.getenv("ENABLE_AUTO_REFRESH", "0") == "1"
    # DEMO MODE (default OFF): when ON and live fetch fails, the app serves
    # clearly-labelled ML-grounded demo readings so all features can be
    # demonstrated while no valid OpenWeather key is available.
    ENABLE_DEMO_DATA = os.getenv("ENABLE_DEMO_DATA", "0") == "1"
    # Concurrency for parallel API requests to OpenWeather
    FETCH_CONCURRENCY = int(os.getenv("FETCH_CONCURRENCY", "10"))
    # Max API requests per refresh cycle (safety cap)
    MAX_CALLS_PER_REFRESH = int(os.getenv("MAX_CALLS_PER_REFRESH", "160"))
    # HTTP timeout (seconds) for outbound calls
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "12"))
    # Minimum seconds between two FORCED refreshes (dashboard open). Protects
    # the OpenWeather free-tier quota when the dashboard is opened repeatedly.
    FORCE_REFRESH_MIN_INTERVAL = int(os.getenv("FORCE_REFRESH_MIN_INTERVAL", "120"))
    # Retry attempts per API call on transient failure
    RETRY_ATTEMPTS = int(os.getenv("RETRY_ATTEMPTS", "2"))

    # --- Application --------------------------------------------------------
    APP_NAME = "AirVision AI"
    APP_VERSION = "1.0.0"
    # CORS origins allowed to talk to this API (comma separated)
    CORS_ORIGINS = os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")

    # --- Paths ---------------------------------------------------------------
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(BASE_DIR)
    DB_PATH = os.getenv("DB_PATH", os.path.join(BASE_DIR, "database", "airvision.db"))
    MODEL_PATH = os.getenv(
        "MODEL_PATH", os.path.join(PROJECT_ROOT, "models", "model.pkl")
    )
    DATASET_PATH = os.getenv(
        "DATASET_PATH", os.path.join(PROJECT_ROOT, "ml", "data", "city_day.csv")
    )
