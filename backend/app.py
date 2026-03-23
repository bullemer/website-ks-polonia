from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional

from mailer import send_email

app = FastAPI(title="KS Polonia API")

# Configure CORS
origins = [
    "https://ks-polonia.de",
    "https://www.ks-polonia.de",
    "http://localhost:4321",
    "http://127.0.0.1:4321"
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
    datenschutz: Optional[str] = "" # Consent
    verbindlich: Optional[str] = "" # Consent
    website_url: Optional[str] = ""  # Honeypot

# --- Endpoint: Contact ---
@app.post("/contact")
async def handle_contact(form: ContactForm):
    # Security: Honeypot Check
    if form.website_url.strip() != "":
        # Silently reject bot but return success
        return JSONResponse({"success": True, "message": "Ihre Nachricht wurde erfolgreich gesendet!"})
        
    # Security: Math CAPTCHA
    try:
        if int(form.captcha_answer.strip()) != int(form.captcha_expected.strip()):
            return JSONResponse({"success": False, "error": "Die Sicherheitsfrage wurde falsch beantwortet. Bitte prüfen Sie Ihre Eingabe."}, status_code=400)
    except ValueError:
        return JSONResponse({"success": False, "error": "Bitte geben Sie eine gültige Zahl als Antwort auf die Sicherheitsfrage ein."}, status_code=400)
    
    # Map subject
    subject_prefix = "Neue Nachricht über die Webseite"
    if form.subject == 'probetraining':
        subject_prefix = "Anfrage Probetraining"
    elif form.subject == 'sponsoring':
        subject_prefix = "Anfrage Sponsoring"
    elif form.subject == 'allgemein':
        subject_prefix = "Allgemeine Anfrage"

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
        subject=email_subject,
        text_body=body,
        reply_to_email=form.email,
        reply_to_name=form.name
    )

    if success:
        return JSONResponse({"success": True, "message": "Ihre Nachricht wurde erfolgreich gesendet!"})
    else:
        return JSONResponse({"success": False, "error": "Die Nachricht konnte nicht gesendet werden. Error: " + error_msg}, status_code=500)

# --- Endpoint: Mitgliedsantrag ---
import os
import datetime
from fastapi import UploadFile

UPLOAD_DIR = "/usr/home/trusteei/kspolonia_uploads"

@app.post("/mitgliedsantrag")
async def handle_membership(request: Request):
    form = await request.form()
    
    # Security: Honeypot Check
    website_url = form.get("website_url", "")
    if isinstance(website_url, str) and website_url.strip() != "":
        return JSONResponse({"success": True, "message": "Ihr Antrag wurde erfolgreich übermittelt!"})
    
    vorname = form.get("vorname", "")
    nachname = form.get("nachname", "")
    email = form.get("email", "")
    
    # Process Files
    # Create upload directory if it doesn't exist (e.g. for local testing)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    id_front = form.get("id_front")
    id_back = form.get("id_back")
    
    if not id_front or not hasattr(id_front, 'filename') or not id_front.filename:
        return JSONResponse({"success": False, "error": f"Bitte laden Sie die Vorderseite Ihres Ausweises hoch."})
        
    if not id_back or not hasattr(id_back, 'filename') or not id_back.filename:
        return JSONResponse({"success": False, "error": f"Bitte laden Sie die Rückseite Ihres Ausweises hoch."})
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    front_filename = f"{nachname}_{vorname}_Front_{timestamp}.jpg"
    back_filename = f"{nachname}_{vorname}_Back_{timestamp}.jpg"
    
    front_path = os.path.join(UPLOAD_DIR, front_filename)
    back_path = os.path.join(UPLOAD_DIR, back_filename)
    
    # Save files
    with open(front_path, "wb") as f_front:
        f_front.write(await id_front.read())
        
    with open(back_path, "wb") as f_back:
        f_back.write(await id_back.read())
        
    email_subject = f"Neuer Mitgliedsantrag online: {vorname} {nachname}"
    
    body = (
        f"Es wurde ein neuer Mitgliedsantrag über das Online-Formular eingereicht:\n\n"
        f"=== 1. ANTRAGSTELLER*IN / MITGLIEDSDATEN ===\n"
        f"Vorname: {vorname}\n"
        f"Nachname: {nachname}\n"
        f"Straße: {form.get('strasse', '')}\n"
        f"PLZ/Ort: {form.get('plz', '')} {form.get('ort', '')}\n"
        f"Land: {form.get('land', '')}\n"
        f"Geburtsdatum: {form.get('geburtsdatum', '')}\n"
        f"Geschlecht: {form.get('geschlecht', '')}\n\n"
        f"=== 2. KONTAKTDATEN ===\n"
        f"E-Mail: {email}\n"
        f"Telefon: {form.get('telefon', '')}\n\n"
        f"=== 3. VEREINSEINTRITT & ABTEILUNGEN ===\n"
        f"Eintrittsdatum: {form.get('eintrittsdatum', '')}\n"
        f"Abteilungen: {form.get('abteilungen', '')}\n\n"
        f"=== 4. ZAHLUNGSART ===\n"
        f"Art: {form.get('zahlungsart', '')}\n\n"
    )

    bemerkungen = form.get('bemerkungen', '')
    trainer_referenz = form.get('trainer_referenz', '')

    if bemerkungen or trainer_referenz:
        body += "=== 5. ZUSATZDATEN ===\n"
        if trainer_referenz:
            body += f"Trainer - Referenz: {trainer_referenz}\n"
        if bemerkungen:
            body += f"Bemerkungen:\n{bemerkungen}\n"
        body += "\n"

    body += (
        f"=== 6. AUSWEISDOKUMENTE (SICHERER UPLOAD) ===\n"
        f"Die hochgeladenen Ausweisbilder wurden im System gespeichert und dieser E-Mail als Anlage beigefügt.\n"
        f"Storage Verzeichnis: /usr/home/trusteei/kspolonia_uploads/\n"
        f"1. Vorderseite: {front_filename}\n"
        f"2. Rückseite: {back_filename}\n\n"
    )

    body += (
        f"=== 7. ZUSTIMMUNGEN ===\n"
        f"✓ DSGVO und BDSG zugestimmt.\n"
        f"✓ Rechtsverbindlichkeit des Antrags bestätigt.\n"
    )

    success, error_msg = send_email(
        subject=email_subject,
        text_body=body,
        reply_to_email=email,
        reply_to_name=f"{vorname} {nachname}",
        attachments=[front_path, back_path]
    )

    if success:
        return JSONResponse({"success": True, "message": "Vielen Dank! Ihr Antrag wurde erfolgreich übermittelt."})
    else:
        return JSONResponse({"success": False, "error": "Der Antrag konnte nicht gesendet werden. Error: " + str(error_msg)}, status_code=500)

# --- Endpoint: DB Health Check ---
import asyncpg
import pydantic

API_VERSION = "1.0.1"
DATABASE_URL = "postgresql://trusteei_0:k6%25KkhF%3B%29FY4@kwnz.your-database.de:5432/kspolonia"

@app.get("/health")
async def health_check():
    """ Verify the application and database connectivity """
    status = {"api": "ok", "version": API_VERSION, "database": "unknown"}
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        val = await conn.fetchval('SELECT 1;')
        await conn.close()
        if val == 1:
            status["database"] = "ok"
    except Exception as e:
        status["database"] = "error"
        status["database_error"] = str(e)

    return JSONResponse(status)

# --- Admin Interface (Teams & Players) ---
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import Depends, status, HTTPException
import secrets
from fastapi.templating import Jinja2Templates
import os

security = HTTPBasic()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "polonia2026")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.get("/admin")
async def admin_dashboard(request: Request, team_id: Optional[str] = None, username: str = Depends(get_current_username)):
    teams = []
    players = []
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        # Fetch all teams for the dropdown
        teams_records = await conn.fetch("SELECT id, mannschaftsart, mannschaftsname, spielklasse FROM teams ORDER BY mannschaftsart, mannschaftsname")
        teams = [dict(record) for record in teams_records]
        
        # If a team is selected, fetch its players
        if team_id:
            try:
                # Security: Validate integer to prevent injection
                t_id = int(team_id)
                players_records = await conn.fetch("""
                    SELECT p.name, p.vorname, p.geburtsdatum, p.passnr, p.spielrecht_ab 
                    FROM players p 
                    JOIN team_player tp ON p.id = tp.player_id 
                    WHERE tp.team_id = $1 
                    ORDER BY p.name, p.vorname
                """, t_id)
                players = [dict(record) for record in players_records]
            except ValueError:
                pass # Invalid team_id, ignore
                
        await conn.close()
    except Exception as e:
        print(f"Database error in admin dashboard: {e}")
        
    return templates.TemplateResponse("admin.html", {
        "request": request, 
        "teams": teams, 
        "players": players, 
        "selected_team_id": team_id or ""
    })
