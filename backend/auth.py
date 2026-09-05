"""
KS Polonia – Authentication helpers.
JWT token creation/verification and password hashing with bcrypt.
"""
import datetime
import secrets
import logging
from typing import Optional

from fastapi import Request, HTTPException
from jose import jwt, JWTError
import bcrypt

from config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_HOURS

logger = logging.getLogger(__name__)

# --- Password hashing (direct bcrypt, no passlib) ---


def hash_password(plain: str) -> str:
    """Hash a plaintext password with bcrypt."""
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        logger.exception("Password verification error")
        return False


# --- JWT tokens ---
def create_access_token(member_id: int, email: str, is_admin: bool = False, role: str = "member") -> str:
    """Create a signed JWT access token with role."""
    now = datetime.datetime.now(datetime.timezone.utc)
    is_admin_flag = is_admin or (role in ("superadmin", "admin"))
    payload = {
        "sub": str(member_id),
        "email": email,
        "is_admin": is_admin_flag,
        "role": role,
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
    Returns dict with keys: member_id, email, role, is_admin, is_superadmin.
    Raises HTTPException 401 if not authenticated.
    """
    token = request.cookies.get("session_token")
    if not token:
        raise HTTPException(status_code=401, detail="Nicht angemeldet")
    try:
        payload = decode_token(token)
        role = payload.get("role")
        is_admin = payload.get("is_admin", False)
        # Infer role if not in legacy token
        if not role:
            role = "superadmin" if is_admin else "member"
        return {
            "member_id": int(payload["sub"]),
            "email": payload["email"],
            "role": role,
            "is_admin": is_admin or (role in ("superadmin", "admin")),
            "is_superadmin": (role == "superadmin"),
        }
    except (JWTError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Sitzung abgelaufen")


def require_admin(request: Request) -> dict:
    """
    Enforces that user is either superadmin or admin.
    Raises HTTPException 403 if member.
    """
    member = get_current_member(request)
    if not member["is_admin"] and member.get("role") not in ("superadmin", "admin"):
        raise HTTPException(status_code=403, detail="Kein Administratorzugang")
    return member


def require_superadmin(request: Request) -> dict:
    """
    Enforces that user is a superadmin.
    Raises HTTPException 403 if not superadmin.
    """
    member = get_current_member(request)
    if member.get("role") != "superadmin":
        raise HTTPException(status_code=403, detail="Nur für Superadministratoren zugänglich")
    return member


async def require_team_admin(request: Request, team_id: int) -> dict:
    """
    Enforces that user is either superadmin or assigned as admin/trainer for the given team.
    Raises HTTPException 403 if neither.
    """
    member = get_current_member(request)
    if member.get("role") == "superadmin":
        return member

    if member.get("role") == "admin":
        from database import get_pool
        pool = await get_pool()
        async with pool.acquire() as conn:
            is_assigned = await conn.fetchval(
                """
                SELECT 1 FROM member_teams
                WHERE member_id = $1 AND team_id = $2 AND status = 'active'
                """,
                member["member_id"], team_id,
            )
            if is_assigned:
                return member

    raise HTTPException(status_code=403, detail="Keine Administrator-Berechtigung für dieses Team")


def generate_token() -> str:
    """Generate a random URL-safe token for email verification / password reset."""
    return secrets.token_urlsafe(32)
