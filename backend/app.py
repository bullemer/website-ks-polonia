"""
KS Polonia Hamburg e.V. – API & Membership System
==================================================
FastAPI application serving:
  - Public endpoints (contact form, membership application, wall of honor)
  - Member portal (login, profile, bank account, password)
  - Admin backoffice (members, divisions, teams, applications)

v2.0 – Membership Management System
"""
from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import JSONResponse, HTMLResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional
import os
import datetime
import secrets
import traceback
import asyncpg
from fastapi.templating import Jinja2Templates

from config import (
    DATABASE_URL, API_VERSION, UPLOAD_DIR,
    ADMIN_USER, ADMIN_PASS, CORS_ORIGINS,
)
from database import get_pool, close_pool
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

app = FastAPI(title="KS Polonia API", version=API_VERSION)

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

# --- Lifecycle ---
@app.on_event("startup")
async def startup():
    """Initialize connection pool on startup."""
    await get_pool()

@app.on_event("shutdown")
async def shutdown():
    """Close connection pool on shutdown."""
    await close_pool()


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
    captcha_expected: Optional[str] = None
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
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


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
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


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
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# ═══════════════════════════════════════
#  CONTACT FORM
# ═══════════════════════════════════════

@app.post("/contact")
@app.post("/contact.php")
@app.post("/probetraining")
async def handle_contact(form: ContactForm):
    if form.website_url and form.website_url.strip() != "":
        return JSONResponse({"success": True, "message": "Ihre Nachricht wurde erfolgreich gesendet!"})

    if form.captcha_answer is not None and form.captcha_expected is not None:
        try:
            if int(form.captcha_answer.strip()) != int(form.captcha_expected.strip()):
                return JSONResponse({"success": False, "error": "Die Sicherheitsfrage wurde falsch beantwortet."}, status_code=400)
        except ValueError:
            return JSONResponse({"success": False, "error": "Bitte geben Sie eine gültige Zahl als Antwort ein."}, status_code=400)

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
        return JSONResponse({"success": True, "message": "Ihre Nachricht wurde erfolgreich gesendet!"})
    return JSONResponse({"success": False, "error": f"Fehler beim E-Mail-Versand: {error_msg or 'Unbekannter Fehler'}"}, status_code=500)



# ═══════════════════════════════════════
#  MEMBERSHIP APPLICATION
#  Now inserts into DB + sends email
# ═══════════════════════════════════════

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
        front_filename = f"{nachname}_{vorname}_Front_{timestamp}.jpg"
        front_path = os.path.join(UPLOAD_DIR, front_filename)
        with open(front_path, "wb") as f:
            f.write(await id_front.read())
        attachments.append(front_path)

    if id_back and hasattr(id_back, "filename") and id_back.filename:
        back_filename = f"{nachname}_{vorname}_Back_{timestamp}.jpg"
        back_path = os.path.join(UPLOAD_DIR, back_filename)
        with open(back_path, "wb") as f:
            f.write(await id_back.read())
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
    except Exception as e:
        # If DB insert fails (e.g., duplicate email), still send email
        member_nr = "DB-FEHLER"
        traceback.print_exc()

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
    return JSONResponse({"success": False, "error": "Fehler: " + str(error_msg)}, status_code=500)


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


@app.get("/admin-legacy")
async def admin_legacy_get(request: Request, team_id: Optional[str] = None):
    try:
        if request.cookies.get("admin_session") != "authorized":
            return _render("admin.html", {"request": request, "authenticated": False})
        teams, players = await _load_teams_and_players(team_id)
        return _render("admin.html", {
            "request": request, "authenticated": True,
            "teams": teams, "players": players,
            "selected_team_id": team_id or "",
        })
    except Exception:
        return PlainTextResponse("Error:\n" + traceback.format_exc(), status_code=500)


@app.post("/admin-legacy")
async def admin_legacy_post(
    request: Request,
    username: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    team_id: Optional[str] = Form(None),
):
    try:
        is_authenticated = request.cookies.get("admin_session") == "authorized"
        if username and password:
            if secrets.compare_digest(username, ADMIN_USER) and secrets.compare_digest(password, ADMIN_PASS):
                is_authenticated = True
            else:
                return _render("admin.html", {
                    "request": request, "authenticated": False,
                    "error": "Falscher Benutzername oder Passwort",
                })
        if not is_authenticated:
            return _render("admin.html", {"request": request, "authenticated": False})
        teams, players = await _load_teams_and_players(team_id)
        response = _render("admin.html", {
            "request": request, "authenticated": True,
            "teams": teams, "players": players,
            "selected_team_id": team_id or "",
        })
        response.set_cookie(key="admin_session", value="authorized", max_age=86400, httponly=True, secure=True)
        return response
    except Exception:
        return PlainTextResponse("Error:\n" + traceback.format_exc(), status_code=500)
