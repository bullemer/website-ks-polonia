"""
KS Polonia – Member portal routes.
Server-rendered portal pages for authenticated members.
"""
import os
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from auth import get_current_member
from services import member_service

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "..", "templates"))

router = APIRouter(prefix="/portal", tags=["portal"])


@router.get("/login")
async def portal_login(request: Request):
    """Show login page (or redirect if already authenticated)."""
    try:
        get_current_member(request)
        return RedirectResponse(url="/api/portal")
    except Exception:
        return templates.TemplateResponse(request, "portal_login.html", {})


@router.get("")
async def portal_dashboard(request: Request):
    """Member dashboard — profile, address, bank, teams, payments, card."""
    try:
        current = get_current_member(request)
    except Exception:
        return RedirectResponse(url="/api/portal/login")

    member = await member_service.get_member_by_id(current["member_id"])
    if not member:
        return RedirectResponse(url="/api/portal/login")

    divisions = await member_service.get_member_divisions(current["member_id"])
    teams = await member_service.get_member_teams(current["member_id"])
    bank = await member_service.get_bank_account(current["member_id"])
    payments = await member_service.get_member_payments(current["member_id"])
    payment_summary = await member_service.get_payment_summary(current["member_id"])

    # Document upload status
    has_id_front = bool(member.get("id_front_path"))
    has_id_back = bool(member.get("id_back_path"))

    # Serialize dates
    for key in ("geburtsdatum", "eintrittsdatum"):
        if member.get(key):
            member[key] = str(member[key])

    return templates.TemplateResponse(request, "portal_dashboard.html", {
        "member": member,
        "divisions": divisions,
        "teams": teams,
        "bank": bank,
        "payments": payments,
        "payment_summary": payment_summary,
        "is_admin": current["is_admin"],
        "has_id_front": has_id_front,
        "has_id_back": has_id_back,
    })
