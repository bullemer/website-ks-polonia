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
@app.post("/api/contact")
async def handle_contact(form: ContactForm):
    # Security: Honeypot Check
    if form.website_url.strip() != "":
        # Silently reject bot but return success
        return JSONResponse({"success": True, "message": "Ihre Nachricht wurde erfolgreich gesendet!"})
    
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
@app.post("/api/mitgliedsantrag")
async def handle_membership(form: MembershipForm):
    # Security: Honeypot Check
    if form.website_url.strip() != "":
        return JSONResponse({"success": True, "message": "Ihr Antrag wurde erfolgreich übermittelt!"})
    
    email_subject = f"Neuer Mitgliedsantrag online: {form.vorname} {form.nachname}"
    
    body = (
        f"Es wurde ein neuer Mitgliedsantrag über das Online-Formular eingereicht:\n\n"
        f"=== 1. ANTRAGSTELLER*IN / MITGLIEDSDATEN ===\n"
        f"Vorname: {form.vorname}\n"
        f"Nachname: {form.nachname}\n"
        f"Straße: {form.strasse}\n"
        f"PLZ/Ort: {form.plz} {form.ort}\n"
        f"Land: {form.land}\n"
        f"Geburtsdatum: {form.geburtsdatum}\n"
        f"Geschlecht: {form.geschlecht}\n\n"
        f"=== 2. KONTAKTDATEN ===\n"
        f"E-Mail: {form.email}\n"
        f"Telefon: {form.telefon}\n\n"
        f"=== 3. VEREINSEINTRITT & ABTEILUNGEN ===\n"
        f"Gewünschtes Eintrittsdatum: {form.eintrittsdatum}\n"
        f"Gewählte Abteilungen: {form.abteilungen}\n\n"
        f"=== 4. ZAHLUNGSART ===\n"
        f"Art: {form.zahlungsart}\n\n"
    )

    if form.bemerkungen or form.trainer_referenz:
        body += "=== 5. ZUSATZDATEN ===\n"
        if form.trainer_referenz:
            body += f"Trainer - Referenz: {form.trainer_referenz}\n"
        if form.bemerkungen:
            body += f"Bemerkungen:\n{form.bemerkungen}\n"
        body += "\n"

    body += (
        f"=== 6. ZUSTIMMUNGEN ===\n"
        f"✓ DSGVO und BDSG zugestimmt.\n"
        f"✓ Rechtsverbindlichkeit des Antrags bestätigt.\n"
    )

    success, error_msg = send_email(
        subject=email_subject,
        text_body=body,
        reply_to_email=form.email,
        reply_to_name=f"{form.vorname} {form.nachname}"
    )

    if success:
        return JSONResponse({"success": True, "message": "Vielen Dank! Ihr Antrag wurde erfolgreich übermittelt. Wir werden uns in Kürze bei Ihnen melden."})
    else:
        return JSONResponse({"success": False, "error": "Der Antrag konnte leider nicht gesendet werden. Error: " + error_msg}, status_code=500)

