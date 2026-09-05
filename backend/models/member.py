"""
Pydantic models for Members.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date


# --- Request models ---

class MemberCreate(BaseModel):
    """Fields submitted via the membership application form."""
    vorname: str
    nachname: str
    email: EmailStr
    telefon: Optional[str] = ""
    strasse: str
    plz: str
    ort: str
    land: str = "Deutschland"
    geburtsdatum: str  # comes as string from form, parsed in service
    geschlecht: str
    eintrittsdatum: str
    abteilungen: Optional[str] = ""
    zahlungsart: Optional[str] = "Überweisung"
    trainer_referenz: Optional[str] = ""
    bemerkungen: Optional[str] = ""


class MemberProfileUpdate(BaseModel):
    """Fields a member can update in their own profile."""
    vorname: Optional[str] = None
    nachname: Optional[str] = None
    telefon: Optional[str] = None
    strasse: Optional[str] = None
    plz: Optional[str] = None
    ort: Optional[str] = None
    land: Optional[str] = None


class MemberAdminUpdate(BaseModel):
    """Fields an admin can update on any member."""
    vorname: Optional[str] = None
    nachname: Optional[str] = None
    email: Optional[str] = None
    telefon: Optional[str] = None
    strasse: Optional[str] = None
    plz: Optional[str] = None
    ort: Optional[str] = None
    land: Optional[str] = None
    geburtsdatum: Optional[str] = None
    geschlecht: Optional[str] = None
    eintrittsdatum: Optional[str] = None
    membership_level: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    trainer_referenz: Optional[str] = None
    bemerkungen: Optional[str] = None


class PasswordChange(BaseModel):
    """Password change request."""
    current_password: str
    new_password: str


class LoginRequest(BaseModel):
    """Login credentials."""
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    """Password reset request."""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Password reset with token."""
    token: str
    new_password: str


class BankAccountUpdate(BaseModel):
    """Bank account / SEPA details."""
    kontoinhaber: str
    iban: str
    bic: Optional[str] = ""
    bank_name: Optional[str] = ""


# --- Response models ---

class MemberResponse(BaseModel):
    """Public member representation (no sensitive fields)."""
    id: int
    mitgliedsnummer: Optional[str] = None
    vorname: str
    nachname: str
    email: str
    telefon: Optional[str] = None
    strasse: Optional[str] = None
    plz: Optional[str] = None
    ort: Optional[str] = None
    land: Optional[str] = None
    geburtsdatum: Optional[date] = None
    geschlecht: Optional[str] = None
    eintrittsdatum: Optional[date] = None
    membership_level: Optional[str] = "regular"
    role: Optional[str] = "member"
    is_admin: bool = False
    is_active: bool = True
    email_verified: bool = False

    class Config:
        from_attributes = True


class MemberListItem(BaseModel):
    """Compact member for list views."""
    id: int
    mitgliedsnummer: Optional[str] = None
    vorname: str
    nachname: str
    email: str
    membership_level: Optional[str] = "regular"
    role: Optional[str] = "member"
    is_active: bool = True
    is_admin: bool = False
    eintrittsdatum: Optional[date] = None
    divisions: Optional[str] = None  # comma-separated division names
