"""
KS Polonia Hamburg e.V. – API & Membership System
==================================================
FastAPI application serving:
  - Public endpoints (contact form, membership application, wall of honor)
  - Member portal (login, profile, bank account, password)
  - Admin backoffice (members, divisions, teams, applications)

v2.0 – Membership Management System
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import JSONResponse, HTMLResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, ValidationError
from typing import Optional
import os
import datetime
import secrets
import traceback
import random
import asyncpg
from jose import jwt as jose_jwt, JWTError
from fastapi.templating import Jinja2Templates

from config import (
    DATABASE_URL, API_VERSION, UPLOAD_DIR,
    CORS_ORIGINS, JWT_SECRET, JWT_ALGORITHM, KS_DEV,
)
from database import get_pool, close_pool
from auth import require_superadmin
from mailer import send_email
from services import member_service

# --- Import route modules ---
from routes.auth_routes import router as auth_router
from routes.member_routes import router as member_router
from routes.admin_routes import router as admin_router
from routes.portal_routes import router as portal_router
from routes.ticket_routes import router as ticket_router
from routes.team_routes import router as team_router

# ═══════════════════════════════════════
#  APP SETUP
# ═══════════════════════════════════════

GENERIC_ERROR_MSG = "Ein Fehler ist aufgetreten. Bitte versuchen Sie es später erneut."

ALLOWED_UPLOAD_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".webp"}
MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and tear down resources."""
    await get_pool()
    yield
    await close_pool()


app = FastAPI(
    title="KS Polonia API",
    version=API_VERSION,
    docs_url="/docs" if KS_DEV else None,
    redoc_url="/redoc" if KS_DEV else None,
    lifespan=lifespan,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["OPTIONS", "POST", "GET", "PUT", "DELETE"],
    allow_headers=["*"],
)

# --- Register route modules ---
app.include_router(auth_router)
app.include_router(member_router)
app.include_router(admin_router)
app.include_router(portal_router)
app.include_router(ticket_router)
app.include_router(team_router)


# ═══════════════════════════════════════
#  CAPTCHA TOKEN HELPERS
# ═══════════════════════════════════════

def _create_captcha_token(answer: int) -> str:
    """Create a signed JWT containing the expected captcha answer and an expiry (5 min)."""
    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        "captcha_answer": answer,
        "exp": now + datetime.timedelta(minutes=5),
    }
    return jose_jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def _verify_captcha_token(token: str, user_answer: int) -> bool:
    """Verify a signed captcha token and compare with the user-supplied answer."""
    try:
        payload = jose_jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return int(payload["captcha_answer"]) == user_answer
    except (JWTError, KeyError, ValueError, TypeError):
        return False


@app.get("/captcha-token")
async def get_captcha_token():
    """Generate a random math captcha and return the question + signed token."""
    a = random.randint(1, 20)
    b = random.randint(1, 20)
    answer = a + b
    token = _create_captcha_token(answer)
    return JSONResponse({"question": f"{a} + {b} = ?", "token": token})


# ═══════════════════════════════════════
#  LEGACY PYDANTIC MODELS
# ═══════════════════════════════════════

class ContactForm(BaseModel):
    name: str
    email: EmailStr
    subject: str = "allgemein"
    message: str
    website_url: Optional[str] = ""  # Honeypot
    captcha_answer: Optional[str] = None
    captcha_token: Optional[str] = None
    sportart: Optional[str] = None
    age: Optional[str] = None


class ReserveSpotRequest(BaseModel):
    spot_id: int
    donor_name: str
    donor_message: Optional[str] = ""
    email: EmailStr


# ═══════════════════════════════════════
#  WALL OF HONOR — Donor Spots API
# ═══════════════════════════════════════

@app.get("/wall/spots")
async def wall_get_spots():
    """Return all donor spots with their current status."""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT id, category, position, donor_name, donor_message, status "
                "FROM donor_spots ORDER BY position"
            )
        spots = [dict(r) for r in rows]
        return JSONResponse({"spots": spots})
    except Exception:
        traceback.print_exc()
        return JSONResponse({"error": GENERIC_ERROR_MSG}, status_code=500)


@app.get("/wall/stats")
async def wall_get_stats():
    """Return aggregate stats for the progress bar."""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT category, status, COUNT(*) as cnt "
                "FROM donor_spots GROUP BY category, status ORDER BY category"
            )

        stats = {}
        total = 0
        taken = 0
        for r in rows:
            cat = r["category"]
            if cat not in stats:
                stats[cat] = {"total": 0, "taken": 0, "reserved": 0, "available": 0}
            stats[cat]["total"] += r["cnt"]
            stats[cat][r["status"]] += r["cnt"]
            total += r["cnt"]
            if r["status"] in ("taken", "reserved"):
                taken += r["cnt"]

        return JSONResponse({
            "total": total,
            "taken": taken,
            "available": total - taken,
            "percent": round((taken / total * 100) if total > 0 else 0, 1),
            "by_category": stats,
        })
    except Exception:
        traceback.print_exc()
        return JSONResponse({"error": GENERIC_ERROR_MSG}, status_code=500)


@app.post("/wall/reserve")
async def wall_reserve_spot(req: ReserveSpotRequest):
    """Reserve a donor spot. Mocks payment flow — returns a transaction ID."""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            # Check availability
            spot = await conn.fetchrow(
                "SELECT id, status, category FROM donor_spots WHERE id = $1", req.spot_id
            )
            if not spot:
                return JSONResponse({"error": "Spot nicht gefunden."}, status_code=404)
            if spot["status"] != "available":
                return JSONResponse({"error": "Dieser Platz ist leider nicht mehr verfügbar."}, status_code=409)

            # Generate transaction ID (mock payment)
            txn_id = f"WOH-{secrets.token_hex(6).upper()}"

            await conn.execute(
                "UPDATE donor_spots SET donor_name=$1, donor_message=$2, status='reserved', "
                "transaction_id=$3, reserved_at=NOW() WHERE id=$4",
                req.donor_name, req.donor_message or "", txn_id, req.spot_id,
            )

        # Send notification email
        email_subject = f"Wall of Honor — Neue Reservierung ({spot['category'].title()})"
        body = (
            f"Neue Reservierung auf der Wall of Honor!\n\n"
            f"Kategorie: {spot['category'].title()}\n"
            f"Spot-ID: {req.spot_id}\n"
            f"Name: {req.donor_name}\n"
            f"E-Mail: {req.email}\n"
            f"Nachricht: {req.donor_message or '—'}\n"
            f"Transaction-ID: {txn_id}\n"
        )
        send_email(subject=email_subject, text_body=body,
                   reply_to_email=req.email, reply_to_name=req.donor_name)

        return JSONResponse({
            "success": True,
            "transaction_id": txn_id,
            "message": "Platz erfolgreich reserviert! Wir melden uns in Kürze.",
            "payment_url": f"/wall-of-honor?txn={txn_id}",
        })
    except Exception:
        traceback.print_exc()
        return JSONResponse({"error": GENERIC_ERROR_MSG}, status_code=500)


# ═══════════════════════════════════════
#  CONTACT FORM
# ═══════════════════════════════════════

@app.post("/contact")
@app.post("/contact.php")
@app.post("/probetraining")
async def handle_contact(request: Request):
    # JavaScript sends JSON; ordinary browser submissions send form fields.
    is_json = request.headers.get("content-type", "").split(";", 1)[0].strip().lower() == "application/json"

    def respond(payload, status_code=200):
        if is_json:
            return JSONResponse(payload, status_code=status_code)
        message = payload.get("message") or payload.get("error", "Die Anfrage konnte nicht verarbeitet werden.")
        from html import escape
        return HTMLResponse(
            '<!doctype html><html lang="de"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>Kontakt – KS Polonia</title></head><body>'
            f'<main><h1>Kontakt</h1><p>{escape(message)}</p>'
            '<p><a href="javascript:history.back()">Zurück zum Formular</a> · '
            '<a href="/kontakt">Kontaktseite</a></p></main></body></html>',
            status_code=status_code,
        )

    try:
        data = await request.json() if is_json else dict(await request.form())
        form = ContactForm.model_validate(data)
    except (ValidationError, ValueError):
        return respond({"success": False, "error": "Bitte prüfen Sie Name, E-Mail-Adresse und Nachricht."}, 422)

    if not form.name.strip() or not form.message.strip():
        return respond({"success": False, "error": "Bitte geben Sie Ihren Namen und eine Nachricht ein."}, 422)

    if form.website_url and form.website_url.strip() != "":
        return respond({"success": True, "message": "Ihre Nachricht wurde erfolgreich gesendet!"})

    # Captcha verification via signed server-side token
    if form.captcha_answer is not None and form.captcha_token is not None:
        try:
            user_answer = int(form.captcha_answer.strip())
            if not _verify_captcha_token(form.captcha_token, user_answer):
                return respond({"success": False, "error": "Die Sicherheitsfrage wurde falsch beantwortet."}, 400)
        except ValueError:
            return respond({"success": False, "error": "Bitte geben Sie eine gültige Zahl als Antwort ein."}, 400)

    subject_map = {
        "probetraining": "Anfrage Probetraining",
        "sponsoring": "Anfrage Sponsoring",
        "allgemein": "Allgemeine Anfrage",
    }
    subject_prefix = subject_map.get(form.subject, "Neue Nachricht über die Webseite")
    if form.sportart:
        subject_prefix += f" ({form.sportart})"
    email_subject = f"{subject_prefix} - von {form.name}"

    details = [
        f"Name: {form.name}",
        f"E-Mail: {form.email}",
    ]
    if form.sportart:
        details.append(f"Sportart: {form.sportart}")
    if form.age:
        details.append(f"Jahrgang / Alter: {form.age}")
    details.append(f"Betreff: {subject_prefix}")

    details_str = "\n".join(details)
    body = (
        f"Du hast eine neue Nachricht über das Kontaktformular der Website erhalten:\n\n"
        f"{details_str}\n\n"
        f"Nachricht:\n"
        f"-------------------------------------------\n"
        f"{form.message}\n"
        f"-------------------------------------------\n"
    )

    success, error_msg = send_email(
        subject=email_subject, text_body=body,
        reply_to_email=form.email, reply_to_name=form.name,
    )
    if success:
        return respond({"success": True, "message": "Ihre Nachricht wurde erfolgreich gesendet!"})
    return respond({"success": False, "error": "Der Versand ist fehlgeschlagen. Bitte versuchen Sie es später erneut oder schreiben Sie an info@ks-polonia.de."}, 500)



# ═══════════════════════════════════════
#  MEMBERSHIP APPLICATION
#  Now inserts into DB + sends email
# ═══════════════════════════════════════

async def _read_upload_safe(upload_file) -> bytes:
    """Read an upload file in chunks, enforcing MAX_UPLOAD_BYTES limit."""
    chunks = []
    total = 0
    while True:
        chunk = await upload_file.read(8192)
        if not chunk:
            break
        total += len(chunk)
        if total > MAX_UPLOAD_BYTES:
            raise ValueError("Datei zu groß (max. 10 MB)")
        chunks.append(chunk)
    return b"".join(chunks)


def _validate_upload_extension(filename: str) -> str:
    """Validate and return the file extension. Raises ValueError for invalid types."""
    ext = os.path.splitext(filename)[1].lower() or ""
    if ext not in ALLOWED_UPLOAD_EXTENSIONS:
        raise ValueError(
            f"Ungültiger Dateityp '{ext}'. Erlaubt: {', '.join(sorted(ALLOWED_UPLOAD_EXTENSIONS))}"
        )
    return ext


@app.post("/mitgliedsantrag")
async def handle_membership(request: Request):
    form = await request.form()

    website_url = form.get("website_url", "")
    if isinstance(website_url, str) and website_url.strip() != "":
        return JSONResponse({"success": True, "message": "Ihr Antrag wurde erfolgreich übermittelt!"})

    vorname = form.get("vorname", "")
    nachname = form.get("nachname", "")
    email = form.get("email", "")

    # --- File uploads (optional) ---
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    id_front = form.get("id_front")
    id_back = form.get("id_back")

    front_path = ""
    back_path = ""
    front_filename = ""
    back_filename = ""
    attachments = []

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    if id_front and hasattr(id_front, "filename") and id_front.filename:
        try:
            ext = _validate_upload_extension(id_front.filename)
        except ValueError as ve:
            return JSONResponse({"success": False, "error": str(ve)}, status_code=400)
        front_filename = f"{nachname}_{vorname}_Front_{timestamp}{ext}"
        front_path = os.path.join(UPLOAD_DIR, front_filename)
        try:
            content = await _read_upload_safe(id_front)
        except ValueError as ve:
            return JSONResponse({"success": False, "error": str(ve)}, status_code=400)
        with open(front_path, "wb") as f:
            f.write(content)
        attachments.append(front_path)

    if id_back and hasattr(id_back, "filename") and id_back.filename:
        try:
            ext = _validate_upload_extension(id_back.filename)
        except ValueError as ve:
            return JSONResponse({"success": False, "error": str(ve)}, status_code=400)
        back_filename = f"{nachname}_{vorname}_Back_{timestamp}{ext}"
        back_path = os.path.join(UPLOAD_DIR, back_filename)
        try:
            content = await _read_upload_safe(id_back)
        except ValueError as ve:
            return JSONResponse({"success": False, "error": str(ve)}, status_code=400)
        with open(back_path, "wb") as f:
            f.write(content)
        attachments.append(back_path)

    # --- Insert into database ---
    try:
        result = await member_service.create_member_from_application(
            vorname=vorname,
            nachname=nachname,
            email=email,
            telefon=form.get("telefon", ""),
            strasse=form.get("strasse", ""),
            plz=form.get("plz", ""),
            ort=form.get("ort", ""),
            land=form.get("land", "Deutschland"),
            geburtsdatum=form.get("geburtsdatum", ""),
            geschlecht=form.get("geschlecht", ""),
            eintrittsdatum=form.get("eintrittsdatum", ""),
            abteilungen=form.get("abteilungen", ""),
            trainer_referenz=form.get("trainer_referenz", ""),
            bemerkungen=form.get("bemerkungen", ""),
            id_front_path=front_path,
            id_back_path=back_path,
        )
        member_nr = result["mitgliedsnummer"]
    except Exception:
        traceback.print_exc()
        return JSONResponse(
            {"success": False, "error": "Datenbankfehler beim Anlegen des Mitgliedsantrags. Bitte versuchen Sie es später erneut."},
            status_code=500,
        )

    # --- Send notification email (keep existing behavior) ---
    email_subject = f"Neuer Mitgliedsantrag online: {vorname} {nachname}"
    body = (
        f"Es wurde ein neuer Mitgliedsantrag über das Online-Formular eingereicht:\n\n"
        f"Mitgliedsnummer: {member_nr}\n\n"
        f"=== 1. ANTRAGSTELLER*IN / MITGLIEDSDATEN ===\n"
        f"Vorname: {vorname}\nNachname: {nachname}\n"
        f"Straße: {form.get('strasse', '')}\n"
        f"PLZ/Ort: {form.get('plz', '')} {form.get('ort', '')}\n"
        f"Land: {form.get('land', '')}\n"
        f"Geburtsdatum: {form.get('geburtsdatum', '')}\n"
        f"Geschlecht: {form.get('geschlecht', '')}\n\n"
        f"=== 2. KONTAKTDATEN ===\n"
        f"E-Mail: {email}\nTelefon: {form.get('telefon', '')}\n\n"
        f"=== 3. VEREINSEINTRITT & ABTEILUNGEN ===\n"
        f"Eintrittsdatum: {form.get('eintrittsdatum', '')}\n"
        f"Abteilungen: {form.get('abteilungen', '')}\n\n"
        f"=== 4. ZAHLUNGSART ===\n"
        f"Art: {form.get('zahlungsart', '')}\n\n"
    )
    bemerkungen = form.get("bemerkungen", "")
    trainer_referenz = form.get("trainer_referenz", "")
    if bemerkungen or trainer_referenz:
        body += "=== 5. ZUSATZDATEN ===\n"
        if trainer_referenz:
            body += f"Trainer - Referenz: {trainer_referenz}\n"
        if bemerkungen:
            body += f"Bemerkungen:\n{bemerkungen}\n"
        body += "\n"

    body += "=== 6. AUSWEISDOKUMENTE ===\n"
    if front_filename or back_filename:
        body += f"Storage: {UPLOAD_DIR}/\n"
        if front_filename:
            body += f"1. Vorderseite: {front_filename}\n"
        if back_filename:
            body += f"2. Rückseite: {back_filename}\n"
    else:
        body += "⚠ Keine Dokumente hochgeladen — Nachreichung über Mitgliederportal ausstehend.\n"
    body += "\n"

    body += (
        f"=== 7. ZUSTIMMUNGEN ===\n"
        f"✓ DSGVO und BDSG zugestimmt.\n"
        f"✓ Rechtsverbindlichkeit des Antrags bestätigt.\n\n"
        f"→ Antrag prüfen im Admin-Portal: /api/admin/applications\n"
    )

    success, error_msg = send_email(
        subject=email_subject, text_body=body,
        reply_to_email=email, reply_to_name=f"{vorname} {nachname}",
        attachments=attachments if attachments else None,
    )
    if success:
        return JSONResponse({"success": True, "message": "Vielen Dank! Ihr Antrag wurde erfolgreich übermittelt."})
    return JSONResponse({"success": False, "error": "Fehler beim E-Mail-Versand. Bitte versuchen Sie es später erneut."}, status_code=500)


# ═══════════════════════════════════════
#  HEALTH CHECK
# ═══════════════════════════════════════

@app.get("/health")
async def health_check():
    status = {"api": "ok", "version": API_VERSION, "database": "unknown"}
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            val = await conn.fetchval("SELECT 1;")
        if val == 1:
            status["database"] = "ok"
    except Exception:
        status["database"] = "error"
    return JSONResponse(status)


# ═══════════════════════════════════════
#  LEGACY ADMIN (keep for backward compat)
# ═══════════════════════════════════════

def _render(template_name, context):
    """Render a Jinja2 template to an HTMLResponse. Safe for FastCGI."""
    tpl = templates.get_template(template_name)
    html = tpl.render(context)
    return HTMLResponse(
        content=html,
        headers={"Cache-Control": "no-store, max-age=0", "Pragma": "no-cache"},
    )


async def _load_teams_and_players(team_id=None):
    """Fetch teams list and optionally players for a given team."""
    teams, players = [], []
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT id, mannschaftsart, mannschaftsname, spielklasse "
                "FROM teams ORDER BY mannschaftsart, mannschaftsname"
            )
            teams = [dict(r) for r in rows]
            if team_id:
                t_id = int(team_id)
                prows = await conn.fetch(
                    "SELECT p.vorname, p.name, p.geburtsdatum, p.passnr, p.spielrecht_ab "
                    "FROM players p JOIN team_player tp ON p.id = tp.player_id "
                    "WHERE tp.team_id = $1 ORDER BY p.name, p.vorname",
                    t_id,
                )
                players = [dict(r) for r in prows]
    except Exception:
        pass  # DB unreachable → show page without data
    return teams, players


@app.api_route("/admin-legacy", methods=["GET", "POST"])
async def admin_legacy(request: Request, team_id: Optional[str] = None):
    # The former cookie was a constant and allowed anyone to bypass login.
    require_superadmin(request)
    teams, players = await _load_teams_and_players(team_id)
    return _render("admin.html", {
        "request": request, "authenticated": True,
        "teams": teams, "players": players, "selected_team_id": team_id or "",
    })
