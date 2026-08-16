"""
Pydantic models for Membership Applications.
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ApplicationReview(BaseModel):
    """Admin action on a pending application."""
    status: str  # 'approved' or 'rejected'
    admin_notes: Optional[str] = ""


class ApplicationResponse(BaseModel):
    """Application with joined member info for admin views."""
    id: int
    member_id: int
    vorname: str
    nachname: str
    email: str
    abteilungen: Optional[str] = None
    status: str
    admin_notes: Optional[str] = None
    reviewed_by: Optional[str] = None
    submitted_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
