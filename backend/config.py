"""
KS Polonia – Central Configuration
All settings in one place. Reads from environment variables with sensible defaults.
"""
import os
import json
from pathlib import Path

# This file lives outside the deployed tree and is never committed.
_SECRET_FILE = Path(os.getenv("KS_POLONIA_SECRET_FILE", "/usr/home/trusteei/.config/kspolonia/secrets.json"))
_private = json.loads(_SECRET_FILE.read_text()) if _SECRET_FILE.exists() else {}

# --- Database ---
DATABASE_URL = _private.get("DATABASE_URL") or os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("Set DATABASE_URL")

# --- JWT Auth ---
JWT_SECRET = os.getenv("JWT_SECRET") or _private.get("JWT_SECRET")
if not JWT_SECRET or len(JWT_SECRET) < 32:
    raise RuntimeError("Set a private JWT_SECRET of at least 32 characters before starting the API")
DONATION_CERTIFICATES_ENABLED = _private.get("DONATION_CERTIFICATES_ENABLED") is True
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", "24"))

# --- SMTP / Email ---
SMTP_HOST = os.getenv("SMTP_HOST", "mail.your-server.de")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "info@ks-polonia.de")
SMTP_PASSWORD = _private.get("SMTP_PASSWORD") or os.getenv("SMTP_PASSWORD")
if not SMTP_PASSWORD:
    raise RuntimeError("Set SMTP_PASSWORD")
TARGET_EMAIL = os.getenv("TARGET_EMAIL", "info@ks-polonia.de")
FROM_EMAIL = os.getenv("FROM_EMAIL", "info@ks-polonia.de")

# --- File uploads ---
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/usr/home/trusteei/kspolonia_uploads")

# --- Site ---
SITE_URL = os.getenv("SITE_URL", "https://www.ks-polonia.de")
API_VERSION = "2.0.0"

# --- Dev mode ---
KS_DEV = os.getenv("KS_DEV", "") == "1"

# --- CORS ---
CORS_ORIGINS = [
    "https://ks-polonia.de",
    "https://www.ks-polonia.de",
]
if KS_DEV:
    CORS_ORIGINS.extend([
        "http://localhost:4321",
        "http://127.0.0.1:4321",
    ])
