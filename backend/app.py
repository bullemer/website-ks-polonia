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
from fastapi import UploadFile
from fastapi.templating import Jinja2Templates

from mailer import send_email

app = FastAPI(title="KS Polonia API")

# --- Configuration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
DATABASE_URL = "postgresql://trusteei_0:k6%25KkhF%3B%29FY4@kwnz.your-database.de:5432/kspolonia"
API_VERSION = "1.0.1"
UPLOAD_DIR = "/usr/home/trusteei/kspolonia_uploads"
ADMIN_USER = "admin"
ADMIN_PASS = "polonia2026"

# --- CORS ---
origins = [
    "https://ks-polonia.de",
    "https://www.ks-polonia.de",
    "http://localhost:4321",
    "http://127.0.0.1:4321",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["OPTIONS", "POST", "GET"],
    allow_headers=["*"],
)

# --- Pydantic Data Models ---
class ContactForm(BaseModel):
    name: str
    email: EmailStr
    subject: str = "allgemein"
    message: str
    website_url: Optional[str] = ""  # Honeypot
    captcha_answer: str
    captcha_expected: str

class MembershipForm(BaseModel):
    vorname: str
    nachname: str
    strasse: str
    plz: str
    ort: str
    land: str
    geburtsdatum: str
    geschlecht: str
    telefon: Optional[str] = ""
    email: EmailStr
    eintrittsdatum: str
    abteilungen: Optional[str] = "Keine ausgewählt"
    zahlungsart: Optional[str] = "Überweisung"
    trainer_referenz: Optional[str] = ""
    bemerkungen: Optional[str] = ""
    datenschutz: Optional[str] = ""
    verbindlich: Optional[str] = ""
    website_url: Optional[str] = ""  # Honeypot

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
        conn = await asyncpg.connect(DATABASE_URL)
        rows = await conn.fetch(
            "SELECT id, category, position, donor_name, donor_message, status "
            "FROM donor_spots ORDER BY position"
        )
        await conn.close()
        spots = [dict(r) for r in rows]
        return JSONResponse({"spots": spots})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/wall/stats")
async def wall_get_stats():
    """Return aggregate stats for the progress bar."""
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        rows = await conn.fetch(
            "SELECT category, status, COUNT(*) as cnt "
            "FROM donor_spots GROUP BY category, status ORDER BY category"
        )
        await conn.close()

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
        conn = await asyncpg.connect(DATABASE_URL)

        # Check availability
        spot = await conn.fetchrow(
            "SELECT id, status, category FROM donor_spots WHERE id = $1", req.spot_id
        )
        if not spot:
            await conn.close()
            return JSONResponse({"error": "Spot nicht gefunden."}, status_code=404)
        if spot["status"] != "available":
            await conn.close()
            return JSONResponse({"error": "Dieser Platz ist leider nicht mehr verfügbar."}, status_code=409)

        # Generate transaction ID (mock payment)
        txn_id = f"WOH-{secrets.token_hex(6).upper()}"

        await conn.execute(
            "UPDATE donor_spots SET donor_name=$1, donor_message=$2, status='reserved', "
            "transaction_id=$3, reserved_at=NOW() WHERE id=$4",
            req.donor_name, req.donor_message or "", txn_id, req.spot_id,
        )
        await conn.close()

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
            "payment_url": f"/wall-of-honor?txn={txn_id}",  # Mock — replace with real payment URL
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# --- Endpoint: Contact ---
@app.post("/contact")
async def handle_contact(form: ContactForm):
    if form.website_url.strip() != "":
        return JSONResponse({"success": True, "message": "Ihre Nachricht wurde erfolgreich gesendet!"})

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
    email_subject = f"{subject_prefix} - von {form.name}"

    body = (
        f"Du hast eine neue Nachricht über das Kontaktformular der Website erhalten:\n\n"
        f"Name: {form.name}\n"
        f"E-Mail: {form.email}\n"
        f"Betreff: {form.subject}\n\n"
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
    return JSONResponse({"success": False, "error": "Fehler: " + error_msg}, status_code=500)


# --- Endpoint: Mitgliedsantrag ---
@app.post("/mitgliedsantrag")
async def handle_membership(request: Request):
    form = await request.form()

    website_url = form.get("website_url", "")
    if isinstance(website_url, str) and website_url.strip() != "":
        return JSONResponse({"success": True, "message": "Ihr Antrag wurde erfolgreich übermittelt!"})

    vorname = form.get("vorname", "")
    nachname = form.get("nachname", "")
    email = form.get("email", "")

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    id_front = form.get("id_front")
    id_back = form.get("id_back")

    if not id_front or not hasattr(id_front, "filename") or not id_front.filename:
        return JSONResponse({"success": False, "error": "Bitte laden Sie die Vorderseite Ihres Ausweises hoch."})
    if not id_back or not hasattr(id_back, "filename") or not id_back.filename:
        return JSONResponse({"success": False, "error": "Bitte laden Sie die Rückseite Ihres Ausweises hoch."})

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    front_filename = f"{nachname}_{vorname}_Front_{timestamp}.jpg"
    back_filename = f"{nachname}_{vorname}_Back_{timestamp}.jpg"
    front_path = os.path.join(UPLOAD_DIR, front_filename)
    back_path = os.path.join(UPLOAD_DIR, back_filename)

    with open(front_path, "wb") as f:
        f.write(await id_front.read())
    with open(back_path, "wb") as f:
        f.write(await id_back.read())

    email_subject = f"Neuer Mitgliedsantrag online: {vorname} {nachname}"
    body = (
        f"Es wurde ein neuer Mitgliedsantrag über das Online-Formular eingereicht:\n\n"
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
    body += (
        f"=== 6. AUSWEISDOKUMENTE (SICHERER UPLOAD) ===\n"
        f"Storage: /usr/home/trusteei/kspolonia_uploads/\n"
        f"1. Vorderseite: {front_filename}\n"
        f"2. Rückseite: {back_filename}\n\n"
        f"=== 7. ZUSTIMMUNGEN ===\n"
        f"✓ DSGVO und BDSG zugestimmt.\n"
        f"✓ Rechtsverbindlichkeit des Antrags bestätigt.\n"
    )

    success, error_msg = send_email(
        subject=email_subject, text_body=body,
        reply_to_email=email, reply_to_name=f"{vorname} {nachname}",
        attachments=[front_path, back_path],
    )
    if success:
        return JSONResponse({"success": True, "message": "Vielen Dank! Ihr Antrag wurde erfolgreich übermittelt."})
    return JSONResponse({"success": False, "error": "Fehler: " + str(error_msg)}, status_code=500)


# --- Endpoint: Health Check ---
@app.get("/health")
async def health_check():
    status = {"api": "ok", "version": API_VERSION, "database": "unknown"}
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        val = await conn.fetchval("SELECT 1;")
        await conn.close()
        if val == 1:
            status["database"] = "ok"
    except Exception:
        status["database"] = "error"
    return JSONResponse(status)


# --- Admin Helper ---
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
        conn = await asyncpg.connect(DATABASE_URL)
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
        await conn.close()
    except Exception:
        pass  # DB unreachable → show page without data
    return teams, players


# --- Admin: GET (show login or dashboard) ---
@app.get("/admin")
async def admin_get(request: Request, team_id: Optional[str] = None):
    try:
        if request.cookies.get("admin_session") != "authorized":
            return _render("admin.html", {"request": request, "authenticated": False})

        teams, players = await _load_teams_and_players(team_id)
        return _render("admin.html", {
            "request": request,
            "authenticated": True,
            "teams": teams,
            "players": players,
            "selected_team_id": team_id or "",
        })
    except Exception:
        return PlainTextResponse("Error:\n" + traceback.format_exc(), status_code=500)


# --- Admin: POST (handle login form) ---
@app.post("/admin")
async def admin_post(
    request: Request,
    username: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    team_id: Optional[str] = Form(None),
):
    try:
        is_authenticated = request.cookies.get("admin_session") == "authorized"

        # Check credentials on login attempt
        if username and password:
            if secrets.compare_digest(username, ADMIN_USER) and secrets.compare_digest(password, ADMIN_PASS):
                is_authenticated = True
            else:
                return _render("admin.html", {
                    "request": request,
                    "authenticated": False,
                    "error": "Falscher Benutzername oder Passwort",
                })

        if not is_authenticated:
            return _render("admin.html", {"request": request, "authenticated": False})

        teams, players = await _load_teams_and_players(team_id)
        response = _render("admin.html", {
            "request": request,
            "authenticated": True,
            "teams": teams,
            "players": players,
            "selected_team_id": team_id or "",
        })
        response.set_cookie(key="admin_session", value="authorized", max_age=86400, httponly=True, secure=True)
        return response
    except Exception:
        return PlainTextResponse("Error:\n" + traceback.format_exc(), status_code=500)
