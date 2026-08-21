"""
KS Polonia – Season Ticket routes.
Public signup, holder auth, ticket display, admin management.
"""
import os
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr
from typing import Optional

from auth import verify_password, hash_password, generate_token
from services import ticket_service
from database import get_pool
from mailer import send_email
from config import SITE_URL, JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_HOURS

from jose import jwt, JWTError
import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "..", "templates"))

router = APIRouter(prefix="/tickets", tags=["tickets"])


# ═══════════════════════════════════════
#  AUTH HELPERS (separate from member auth)
# ═══════════════════════════════════════

def _create_ticket_token(holder_id: int, email: str) -> str:
    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        "sub": str(holder_id),
        "email": email,
        "type": "ticket_holder",
        "iat": now,
        "exp": now + datetime.timedelta(hours=int(JWT_EXPIRE_HOURS)),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def _get_current_holder(request: Request) -> dict:
    token = request.cookies.get("ticket_session")
    if not token:
        raise HTTPException(status_code=401, detail="Nicht angemeldet")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "ticket_holder":
            raise HTTPException(status_code=401)
        return {"holder_id": int(payload["sub"]), "email": payload["email"]}
    except (JWTError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Sitzung abgelaufen")


# ═══════════════════════════════════════
#  PUBLIC: Signup / Apply for Season Ticket
# ═══════════════════════════════════════

class TicketSignupRequest(BaseModel):
    vorname: str
    nachname: str
    email: EmailStr
    telefon: Optional[str] = ""


@router.get("/signup")
async def ticket_signup_page(request: Request):
    """Show the season ticket signup form."""
    # If already logged in, redirect
    try:
        _get_current_holder(request)
        return RedirectResponse(url="/api/tickets/my")
    except Exception:
        pass
    return templates.TemplateResponse(request, "ticket_signup.html", {
        "season": ticket_service.CURRENT_SEASON,
    })


@router.post("/apply")
async def ticket_apply(data: TicketSignupRequest):
    """Apply for a season ticket."""
    result = await ticket_service.create_holder_and_apply(
        vorname=data.vorname,
        nachname=data.nachname,
        email=data.email,
        telefon=data.telefon or "",
    )

    if result["already_exists"]:
        status = result["status"]
        if status == "approved":
            return JSONResponse({"success": True, "message": "Sie haben bereits eine genehmigte Dauerkarte für diese Saison. Bitte melden Sie sich an."})
        elif status == "pending":
            return JSONResponse({"success": True, "message": "Ihr Antrag liegt bereits vor und wird bearbeitet."})
        else:
            return JSONResponse({"success": True, "message": "Es liegt bereits ein Antrag für diese Saison vor."})

    # Send notification to admin
    body = (
        f"Neue Dauerkarten-Anfrage!\n\n"
        f"Name: {data.vorname} {data.nachname}\n"
        f"E-Mail: {data.email}\n"
        f"Telefon: {data.telefon or '—'}\n"
        f"Saison: {ticket_service.CURRENT_SEASON}\n\n"
        f"→ Verwalten: {SITE_URL}/api/admin/tickets\n"
    )
    send_email(subject=f"Dauerkarten-Antrag: {data.vorname} {data.nachname}", text_body=body)

    return JSONResponse({
        "success": True,
        "message": "Vielen Dank! Ihr Dauerkarten-Antrag wurde eingereicht. Sie erhalten eine E-Mail, sobald er bearbeitet wurde.",
    })


# ═══════════════════════════════════════
#  AUTH: Login / Logout for ticket holders
# ═══════════════════════════════════════

class TicketLoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.get("/login")
async def ticket_login_page(request: Request):
    try:
        _get_current_holder(request)
        return RedirectResponse(url="/api/tickets/my")
    except Exception:
        pass
    return templates.TemplateResponse(request, "ticket_login.html", {})


@router.post("/login")
async def ticket_login(req: TicketLoginRequest):
    holder = await ticket_service.get_holder_by_email(req.email)
    if not holder or not holder.get("password_hash"):
        raise HTTPException(status_code=401, detail="Ungültige Anmeldedaten")
    if not holder["is_active"]:
        raise HTTPException(status_code=403, detail="Konto deaktiviert")
    if not verify_password(req.password, holder["password_hash"]):
        raise HTTPException(status_code=401, detail="Ungültige Anmeldedaten")

    token = _create_ticket_token(holder["id"], holder["email"])
    response = JSONResponse({
        "success": True,
        "message": f"Willkommen, {holder['vorname']}!",
    })
    response.set_cookie(
        key="ticket_session", value=token,
        max_age=86400, httponly=True, secure=True, samesite="lax",
    )
    return response


@router.post("/logout")
async def ticket_logout():
    response = RedirectResponse(url="/api/tickets/login", status_code=302)
    response.delete_cookie("ticket_session")
    return response


# ═══════════════════════════════════════
#  HOLDER PORTAL: View my tickets
# ═══════════════════════════════════════

@router.get("/my")
async def ticket_my_page(request: Request):
    """Show the ticket holder's portal with their tickets."""
    try:
        current = _get_current_holder(request)
    except Exception:
        return RedirectResponse(url="/api/tickets/login")

    holder = await ticket_service.get_holder_by_id(current["holder_id"])
    if not holder:
        return RedirectResponse(url="/api/tickets/login")

    tickets = await ticket_service.get_holder_tickets(current["holder_id"])

    return templates.TemplateResponse(request, "ticket_portal.html", {
        "holder": holder,
        "tickets": tickets,
    })


# ═══════════════════════════════════════
#  ADMIN: Manage season tickets
# ═══════════════════════════════════════

@router.get("/admin")
async def ticket_admin_page(request: Request):
    """Admin page for managing season tickets (reuses member admin auth)."""
    from auth import require_admin
    admin = require_admin(request)

    pending = await ticket_service.get_pending_tickets()
    all_tickets = await ticket_service.get_all_tickets(season=ticket_service.CURRENT_SEASON)

    return templates.TemplateResponse(request, "ticket_admin.html", {
        "pending": pending,
        "all_tickets": all_tickets,
        "season": ticket_service.CURRENT_SEASON,
        "admin": admin,
    })


class TicketReviewRequest(BaseModel):
    status: str  # approved or rejected
    seat_info: Optional[str] = ""
    price: Optional[float] = None
    admin_notes: Optional[str] = ""


@router.put("/{ticket_id}")
async def ticket_review(request: Request, ticket_id: int, data: TicketReviewRequest):
    from auth import require_admin
    admin = require_admin(request)

    if data.status == "approved":
        result = await ticket_service.approve_ticket(
            ticket_id, admin["email"],
            seat_info=data.seat_info or "", price=data.price,
        )
        if not result:
            raise HTTPException(status_code=404, detail="Ticket nicht gefunden oder bereits bearbeitet")

        # Generate PDF ticket
        from services.ticket_pdf import generate_ticket_pdf
        from config import UPLOAD_DIR
        import os

        pdf_bytes = generate_ticket_pdf(
            vorname=result["vorname"],
            nachname=result["nachname"],
            ticket_code=result["ticket_code"],
            season=result["season"],
            seat_info=data.seat_info or "",
        )

        # Save PDF to disk
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        pdf_filename = f"Dauerkarte_{result['ticket_code'].replace('-', '_')}.pdf"
        pdf_path = os.path.join(UPLOAD_DIR, pdf_filename)
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)

        # Send approval email with PDF attachment
        body = (
            f"Hallo {result['vorname']},\n\n"
            f"Ihre Dauerkarte für die Saison {result['season']} wurde genehmigt! 🎉\n\n"
            f"Ticket-Nummer: {result['ticket_code']}\n\n"
            f"Ihre digitale Dauerkarte finden Sie als PDF im Anhang dieser E-Mail.\n"
            f"Sie können sie auch jederzeit online anzeigen:\n"
            f"{SITE_URL}/api/tickets/login\n\n"
        )
        if result["temp_password"]:
            body += (
                f"Ihre Zugangsdaten:\n"
                f"E-Mail: {result['email']}\n"
                f"Passwort: {result['temp_password']}\n\n"
                f"Bitte ändern Sie Ihr Passwort nach der ersten Anmeldung.\n\n"
            )
        else:
            body += "Melden Sie sich mit Ihren bestehenden Zugangsdaten an.\n\n"

        body += "Sportliche Grüße,\nKS Polonia Hamburg e.V."

        send_email(
            subject=f"Dauerkarte genehmigt – {result['season']}",
            text_body=body,
            to_email=result["email"],
            attachments=[pdf_path],
        )
        return JSONResponse({"success": True, "message": f"Genehmigt. PDF + E-Mail an {result['email']} gesendet."})

    elif data.status == "rejected":
        ok = await ticket_service.reject_ticket(ticket_id, admin["email"], data.admin_notes or "")
        if not ok:
            raise HTTPException(status_code=404)
        return JSONResponse({"success": True, "message": "Abgelehnt"})

    raise HTTPException(status_code=400, detail="Status: 'approved' oder 'rejected'")
