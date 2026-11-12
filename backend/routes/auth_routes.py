"""
KS Polonia – Auth routes.
Login, logout, password reset, email verification, account activation.
"""
import os
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr
from typing import Optional

from auth import (
    verify_password, hash_password, create_access_token,
    get_current_member, generate_token,
)
from models.member import LoginRequest, ForgotPasswordRequest, ResetPasswordRequest
from services import member_service
from mailer import send_email
from config import SITE_URL

router = APIRouter(prefix="/auth", tags=["auth"])

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "..", "templates"))


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


@router.api_route("/logout", methods=["GET", "POST"])
async def logout(request: Request):
    """Clear the JWT cookie and redirect to login page (or return JSON)."""
    is_json = "application/json" in request.headers.get("accept", "") or request.method == "POST"
    if is_json:
        response = JSONResponse({"success": True, "message": "Erfolgreich abgemeldet"})
    else:
        response = RedirectResponse(url="/api/portal/login", status_code=302)
    response.delete_cookie(
        key="session_token",
        path="/",
        httponly=True,
        secure=True,
        samesite="lax",
    )
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
    ok, err = send_email(
        subject="KS Polonia – Passwort zurücksetzen",
        text_body=body,
        to_email=member["email"],
    )
    if not ok:
        print(f"Email error: {err}")

    return JSONResponse({"success": True, "message": "Falls ein Konto existiert, wurde eine E-Mail versendet."})


@router.get("/reset-form")
async def reset_form(request: Request, token: str = ""):
    """Render the password-reset form. Validates the token first."""
    error = None
    if not token:
        error = "Kein Token angegeben. Bitte fordern Sie einen neuen Link an."
    else:
        from database import get_pool
        pool = await get_pool()
        async with pool.acquire() as conn:
            member = await conn.fetchrow(
                """
                SELECT id FROM members
                WHERE password_reset_token = $1
                  AND password_reset_expires > NOW()
                """,
                token,
            )
            if not member:
                error = "Dieser Link ist ungültig oder abgelaufen. Bitte fordern Sie einen neuen Link an."

    return templates.TemplateResponse(request, "reset_password.html", {
        "token": token,
        "error": error,
    })


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

        if len(req.new_password) < 8:
            raise HTTPException(status_code=400, detail="Passwort muss mindestens 8 Zeichen lang sein")

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


# ═══════════════════════════════════════
#  ACCOUNT ACTIVATION (Nachname + Geburtsdatum)
# ═══════════════════════════════════════

class RequestAccessRequest(BaseModel):
    nachname: str
    geburtsdatum: str  # YYYY-MM-DD
    email: EmailStr


class ActivateLookupRequest(BaseModel):
    nachname: str
    geburtsdatum: str  # YYYY-MM-DD


class ActivateCompleteRequest(BaseModel):
    activate_token: str
    email: EmailStr
    telefon: Optional[str] = None
    password: str


@router.post("/activate-lookup")
async def activate_lookup(req: ActivateLookupRequest):
    """
    Step 1: Member identifies by Nachname + Geburtsdatum.
    Returns a short-lived activate_token tied to that member.
    Only works for active members who have NOT yet set an email.
    """
    from database import get_pool
    import datetime

    # Validate date format
    try:
        dob = datetime.date.fromisoformat(req.geburtsdatum)
    except ValueError:
        raise HTTPException(status_code=400, detail="Ungültiges Datumsformat.")

    pool = await get_pool()
    async with pool.acquire() as conn:
        # Case-insensitive last-name match + exact DOB
        member = await conn.fetchrow(
            """
            SELECT id, vorname, nachname, email
            FROM members
            WHERE LOWER(nachname) = LOWER($1)
              AND geburtsdatum = $2
              AND is_active = TRUE
            ORDER BY id
            LIMIT 1
            """,
            req.nachname.strip(), dob,
        )

    if not member:
        raise HTTPException(
            status_code=404,
            detail="Kein Mitglied mit diesem Namen und Geburtsdatum gefunden. "
                   "Bitte überprüfe die Eingabe oder wende dich an den Verein.",
        )

    if member["email"]:
        raise HTTPException(
            status_code=409,
            detail="Für dieses Mitglied ist bereits eine E-Mail-Adresse hinterlegt. "
                   "Bitte nutze 'Passwort vergessen', um dein Passwort zurückzusetzen.",
        )

    # Generate a short-lived activate token and store it
    token = generate_token()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE members
            SET claim_token = $1, updated_at = NOW()
            WHERE id = $2
            """,
            token, member["id"],
        )

    return JSONResponse({
        "success": True,
        "vorname": member["vorname"],
        "activate_token": token,
    })


@router.post("/activate-complete")
async def activate_complete(req: ActivateCompleteRequest):
    """
    Step 2: Member sets email + password using the activate_token from step 1.
    """
    from database import get_pool

    if len(req.password) < 8:
        raise HTTPException(status_code=400, detail="Passwort muss mindestens 8 Zeichen lang sein.")

    pool = await get_pool()
    async with pool.acquire() as conn:
        member = await conn.fetchrow(
            """
            SELECT id, email, vorname
            FROM members
            WHERE claim_token = $1 AND is_active = TRUE
            """,
            req.activate_token,
        )

    if not member:
        raise HTTPException(status_code=400, detail="Ungültiger oder abgelaufener Aktivierungslink.")

    if member["email"]:
        raise HTTPException(status_code=409, detail="Konto wurde bereits aktiviert.")

    # Check email not already taken
    async with pool.acquire() as conn:
        existing = await conn.fetchrow(
            "SELECT id FROM members WHERE email = $1 AND id != $2",
            req.email, member["id"],
        )
        if existing:
            raise HTTPException(
                status_code=409,
                detail="Diese E-Mail-Adresse ist bereits einem anderen Mitglied zugeordnet.",
            )

    # Update member: set email, phone, password, clear token
    hashed = hash_password(req.password)
    async with pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE members
            SET email = $1,
                telefon = COALESCE($2, telefon),
                password_hash = $3,
                claim_token = NULL,
                email_verified = TRUE,
                updated_at = NOW()
            WHERE id = $4
            """,
            req.email,
            req.telefon,
            hashed,
            member["id"],
        )

    return JSONResponse({
        "success": True,
        "message": f"Konto für {member['vorname']} erfolgreich aktiviert!",
    })


# ═══════════════════════════════════════
#  REQUEST ACCESS (Zugang anfordern)
# ═══════════════════════════════════════

@router.post("/request-access")
async def request_access(req: RequestAccessRequest):
    """
    Single-step flow: member provides Nachname + Geburtsdatum + Email.
    A random password is generated, stored, and emailed to the member.
    """
    import datetime
    import secrets

    # Validate date format
    try:
        dob = datetime.date.fromisoformat(req.geburtsdatum)
    except ValueError:
        raise HTTPException(status_code=400, detail="Ungültiges Datumsformat.")

    from database import get_pool
    pool = await get_pool()

    async with pool.acquire() as conn:
        # Case-insensitive last-name match + exact DOB
        member = await conn.fetchrow(
            """
            SELECT id, vorname, nachname, email
            FROM members
            WHERE LOWER(nachname) = LOWER($1)
              AND geburtsdatum = $2
              AND is_active = TRUE
            ORDER BY id
            LIMIT 1
            """,
            req.nachname.strip(), dob,
        )

    if not member:
        raise HTTPException(
            status_code=404,
            detail="Kein Mitglied gefunden.",
        )

    email = req.email.strip().lower()

    # Check email not already taken by a DIFFERENT member
    async with pool.acquire() as conn:
        existing = await conn.fetchrow(
            "SELECT id FROM members WHERE email = $1 AND id != $2",
            email, member["id"],
        )
        if existing:
            raise HTTPException(
                status_code=409,
                detail="E-Mail bereits vergeben.",
            )

    # Generate random password
    pw = secrets.token_urlsafe(10)[:10]
    hashed = hash_password(pw)

    # Update member record
    async with pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE members
            SET email = $1,
                password_hash = $2,
                email_verified = TRUE,
                updated_at = NOW()
            WHERE id = $3
            """,
            email, hashed, member["id"],
        )

    # Send credentials email
    body = (
        f"Hallo {member['vorname']},\n\n"
        f"dein Zugang zum KS Polonia Mitgliederportal wurde eingerichtet.\n\n"
        f"Deine Zugangsdaten:\n"
        f"E-Mail: {email}\n"
        f"Passwort: {pw}\n\n"
        f"Bitte ändere dein Passwort nach dem ersten Login.\n\n"
        f"Login: {SITE_URL}/portal/login\n\n"
        f"Sportliche Grüße,\n"
        f"KS Polonia Hamburg"
    )
    ok, err = send_email(
        subject="Dein KS Polonia Zugang",
        text_body=body,
        to_email=email,
    )
    if not ok:
        print(f"Email error: {err}")

    return JSONResponse({
        "success": True,
        "message": "Zugangsdaten wurden per E-Mail versendet.",
    })
