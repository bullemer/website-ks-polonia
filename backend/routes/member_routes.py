"""
KS Polonia – Member self-service routes.
Profile view/edit, bank account, password change, division/team info.
"""
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse

from auth import get_current_member, verify_password, hash_password
from models.member import MemberProfileUpdate, PasswordChange, BankAccountUpdate
from services import member_service

router = APIRouter(prefix="/member", tags=["member"])


@router.get("/profile")
async def get_profile(request: Request):
    """Get the current member's full profile."""
    current = get_current_member(request)
    member = await member_service.get_member_by_id(current["member_id"])
    if not member:
        raise HTTPException(status_code=404, detail="Mitglied nicht gefunden")

    # Strip sensitive fields
    safe_fields = {
        "id", "mitgliedsnummer", "vorname", "nachname", "email", "telefon",
        "strasse", "plz", "ort", "land", "geburtsdatum", "geschlecht",
        "eintrittsdatum", "membership_level", "is_admin", "email_verified",
    }
    profile = {k: v for k, v in member.items() if k in safe_fields}

    # Serialize dates
    for key in ("geburtsdatum", "eintrittsdatum"):
        if profile.get(key):
            profile[key] = str(profile[key])

    return profile


@router.put("/profile")
async def update_profile(request: Request, updates: MemberProfileUpdate):
    """Update the current member's profile (address, phone, etc.)."""
    current = get_current_member(request)
    update_dict = updates.model_dump(exclude_none=True)
    if not update_dict:
        raise HTTPException(status_code=400, detail="Keine Änderungen angegeben")

    success = await member_service.update_member_profile(current["member_id"], update_dict)
    if success:
        return JSONResponse({"success": True, "message": "Profil aktualisiert"})
    raise HTTPException(status_code=500, detail="Fehler beim Speichern")


@router.put("/password")
async def change_password(request: Request, data: PasswordChange):
    """Change the current member's password."""
    current = get_current_member(request)
    member = await member_service.get_member_by_id(current["member_id"])

    if not member or not verify_password(data.current_password, member["password_hash"]):
        raise HTTPException(status_code=400, detail="Aktuelles Passwort ist falsch")

    if len(data.new_password) < 8:
        raise HTTPException(status_code=400, detail="Neues Passwort muss mindestens 8 Zeichen haben")

    hashed = hash_password(data.new_password)
    await member_service.update_member_profile(
        current["member_id"], {"password_hash": hashed}
    )

    return JSONResponse({"success": True, "message": "Passwort erfolgreich geändert"})


@router.get("/bank-account")
async def get_bank(request: Request):
    """Get the current member's active bank account."""
    current = get_current_member(request)
    account = await member_service.get_bank_account(current["member_id"])
    if not account:
        return JSONResponse({"bank_account": None})

    return {
        "bank_account": {
            "kontoinhaber": account["kontoinhaber"],
            "iban": account["iban"],
            "bic": account.get("bic", ""),
            "bank_name": account.get("bank_name", ""),
            "is_sepa_mandate": account.get("is_sepa_mandate", False),
        }
    }


@router.put("/bank-account")
async def update_bank(request: Request, data: BankAccountUpdate):
    """Update (replace) the current member's bank account."""
    current = get_current_member(request)

    # Basic IBAN validation
    iban = data.iban.replace(" ", "").upper()
    if len(iban) < 15 or len(iban) > 34:
        raise HTTPException(status_code=400, detail="Ungültige IBAN")

    new_id = await member_service.update_bank_account(
        current["member_id"],
        kontoinhaber=data.kontoinhaber,
        iban=iban,
        bic=data.bic or "",
        bank_name=data.bank_name or "",
    )

    return JSONResponse({"success": True, "message": "Bankverbindung aktualisiert", "id": new_id})


@router.get("/divisions")
async def get_divisions(request: Request):
    """Get the current member's division memberships."""
    current = get_current_member(request)
    divisions = await member_service.get_member_divisions(current["member_id"])

    # Serialize dates
    for d in divisions:
        for key in ("joined_at",):
            if d.get(key):
                d[key] = str(d[key])

    return {"divisions": divisions}


@router.get("/teams")
async def get_teams(request: Request):
    """Get the current member's team assignments."""
    current = get_current_member(request)
    teams = await member_service.get_member_teams(current["member_id"])

    for t in teams:
        for key in ("joined_at",):
            if t.get(key):
                t[key] = str(t[key])

    return {"teams": teams}
