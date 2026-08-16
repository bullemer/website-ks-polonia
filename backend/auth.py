"""
KS Polonia – Authentication helpers.
JWT token creation/verification and password hashing with bcrypt.
"""
import datetime
import secrets
from typing import Optional

from fastapi import Request, HTTPException
from jose import jwt, JWTError
from passlib.context import CryptContext

from config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_HOURS

# --- Password hashing ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """Hash a plaintext password with bcrypt."""
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return pwd_context.verify(plain, hashed)


# --- JWT tokens ---
def create_access_token(member_id: int, email: str, is_admin: bool = False) -> str:
    """Create a signed JWT access token."""
    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        "sub": str(member_id),
        "email": email,
        "is_admin": is_admin,
        "iat": now,
        "exp": now + datetime.timedelta(hours=JWT_EXPIRE_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and verify a JWT token. Raises JWTError on failure."""
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])


# --- Request helpers ---
def get_current_member(request: Request) -> dict:
    """
    Extract the current member from the JWT cookie.
    Returns dict with keys: member_id, email, is_admin.
    Raises HTTPException 401 if not authenticated.
    """
    token = request.cookies.get("session_token")
    if not token:
        raise HTTPException(status_code=401, detail="Nicht angemeldet")
    try:
        payload = decode_token(token)
        return {
            "member_id": int(payload["sub"]),
            "email": payload["email"],
            "is_admin": payload.get("is_admin", False),
        }
    except (JWTError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Sitzung abgelaufen")


def require_admin(request: Request) -> dict:
    """
    Like get_current_member but also enforces is_admin=True.
    Raises HTTPException 403 if not admin.
    """
    member = get_current_member(request)
    if not member["is_admin"]:
        raise HTTPException(status_code=403, detail="Kein Administratorzugang")
    return member


def generate_token() -> str:
    """Generate a random URL-safe token for email verification / password reset."""
    return secrets.token_urlsafe(32)
