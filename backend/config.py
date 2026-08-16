"""
KS Polonia – Central Configuration
All settings in one place. Reads from environment variables with sensible defaults.
"""
import os

# --- Database ---
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://trusteei_0:k6%25KkhF%3B%29FY4@kwnz.your-database.de:5432/kspolonia",
)

# --- JWT Auth ---
JWT_SECRET = os.getenv("JWT_SECRET", "ks-polonia-jwt-secret-change-in-production-2026")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", "24"))

# --- Admin bootstrap ---
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "polonia2026")

# --- SMTP / Email ---
SMTP_HOST = os.getenv("SMTP_HOST", "mail.your-server.de")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "info@ks-polonia.de")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "C4XOidAid08XX7U6")
TARGET_EMAIL = os.getenv("TARGET_EMAIL", "info@ks-polonia.de")
FROM_EMAIL = os.getenv("FROM_EMAIL", "info@ks-polonia.de")

# --- File uploads ---
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/usr/home/trusteei/kspolonia_uploads")

# --- Site ---
SITE_URL = os.getenv("SITE_URL", "https://www.ks-polonia.de")
API_VERSION = "2.0.0"

# --- CORS ---
CORS_ORIGINS = [
    "https://ks-polonia.de",
    "https://www.ks-polonia.de",
    "http://localhost:4321",
    "http://127.0.0.1:4321",
]
