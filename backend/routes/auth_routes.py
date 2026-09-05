"""
KS Polonia – Auth routes.
Login, logout, password reset, email verification.
"""
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse

from auth import (
    verify_password, hash_password, create_access_token,
    get_current_member, generate_token,
)
from models.member import LoginRequest, ForgotPasswordRequest, ResetPasswordRequest
from services import member_service
from mailer import send_email
from config import SITE_URL

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(req: LoginRequest):
    """Authenticate with email + password, set JWT cookie."""
    member = await member_service.get_member_by_email(req.email)
    if not member or not member.get("password_hash"):
        raise HTTPException(status_code=401, detail="Ungültige Anmeldedaten")

    if not member["is_active"]:
        raise HTTPException(status_code=403, detail="Ihr Konto ist deaktiviert. Bitte kontaktieren Sie den Verein.")

    if not verify_password(req.password, member["password_hash"]):
        raise HTTPException(status_code=401, detail="Ungültige Anmeldedaten")

    role = member.get("role") or ("superadmin" if member.get("is_admin") else "member")
    token = create_access_token(
        member_id=member["id"],
        email=member["email"],
        is_admin=member.get("is_admin", False),
        role=role,
    )

    response = JSONResponse({
        "success": True,
        "message": f"Willkommen, {member['vorname']}!",
        "role": role,
        "is_admin": member.get("is_admin", False) or (role in ("superadmin", "admin")),
        "is_superadmin": (role == "superadmin"),
    })
    response.set_cookie(
        key="session_token",
        value=token,
        max_age=86400,
        httponly=True,
        secure=True,
        samesite="lax",
    )
    return response


@router.get("/logout")
async def logout():
    """Clear the JWT cookie and redirect to login page."""
    response = RedirectResponse(url="/api/portal/login", status_code=302)
    response.delete_cookie("session_token")
    return response


@router.get("/me")
async def me(request: Request):
    """Get current authenticated member info."""
    current = get_current_member(request)
    member = await member_service.get_member_by_id(current["member_id"])
    if not member:
        raise HTTPException(status_code=404, detail="Mitglied nicht gefunden")

    role = member.get("role") or ("superadmin" if member.get("is_admin") else "member")
    return {
        "id": member["id"],
        "mitgliedsnummer": member["mitgliedsnummer"],
        "vorname": member["vorname"],
        "nachname": member["nachname"],
        "email": member["email"],
        "role": role,
        "is_admin": member.get("is_admin", False) or (role in ("superadmin", "admin")),
        "is_superadmin": (role == "superadmin"),
        "membership_level": member["membership_level"],
    }


@router.post("/forgot-password")
async def forgot_password(req: ForgotPasswordRequest):
    """Send a password reset email."""
    member = await member_service.get_member_by_email(req.email)

    # Always return success to avoid email enumeration
    if not member:
        return JSONResponse({"success": True, "message": "Falls ein Konto existiert, wurde eine E-Mail versendet."})

    token = generate_token()
    from database import get_pool
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE members
            SET password_reset_token = $1,
                password_reset_expires = NOW() + INTERVAL '2 hours'
            WHERE id = $2
            """,
            token, member["id"],
        )

    reset_url = f"{SITE_URL}/api/auth/reset-form?token={token}"
    body = (
        f"Hallo {member['vorname']},\n\n"
        f"Sie haben ein neues Passwort für Ihr KS Polonia Konto angefordert.\n\n"
        f"Klicken Sie auf folgenden Link, um Ihr Passwort zurückzusetzen:\n"
        f"{reset_url}\n\n"
        f"Dieser Link ist 2 Stunden gültig.\n\n"
        f"Falls Sie diese Anfrage nicht gestellt haben, ignorieren Sie diese E-Mail.\n\n"
        f"Sportliche Grüße,\nKS Polonia Hamburg e.V."
    )
    send_email(
        subject="KS Polonia – Passwort zurücksetzen",
        text_body=body,
        reply_to_email=member["email"],
        reply_to_name=f"{member['vorname']} {member['nachname']}",
    )

    return JSONResponse({"success": True, "message": "Falls ein Konto existiert, wurde eine E-Mail versendet."})


@router.post("/reset-password")
async def reset_password(req: ResetPasswordRequest):
    """Reset password with a valid token."""
    from database import get_pool
    pool = await get_pool()
    async with pool.acquire() as conn:
        member = await conn.fetchrow(
            """
            SELECT id, vorname FROM members
            WHERE password_reset_token = $1
              AND password_reset_expires > NOW()
            """,
            req.token,
        )
        if not member:
            raise HTTPException(status_code=400, detail="Ungültiger oder abgelaufener Link.")

        hashed = hash_password(req.new_password)
        await conn.execute(
            """
            UPDATE members
            SET password_hash = $1, password_reset_token = NULL, password_reset_expires = NULL,
                updated_at = NOW()
            WHERE id = $2
            """,
            hashed, member["id"],
        )

    return JSONResponse({"success": True, "message": "Passwort erfolgreich geändert. Sie können sich jetzt anmelden."})


@router.get("/verify-email/{token}")
async def verify_email(token: str):
    """Verify email address via token link."""
    from database import get_pool
    pool = await get_pool()
    async with pool.acquire() as conn:
        member = await conn.fetchrow(
            "SELECT id FROM members WHERE email_verify_token = $1",
            token,
        )
        if not member:
            raise HTTPException(status_code=400, detail="Ungültiger Bestätigungslink.")

        await conn.execute(
            """
            UPDATE members
            SET email_verified = TRUE, email_verify_token = NULL, updated_at = NOW()
            WHERE id = $1
            """,
            member["id"],
        )

    return RedirectResponse(url=f"{SITE_URL}/portal/login?verified=1")
