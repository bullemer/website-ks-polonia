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
        return templates.TemplateResponse("portal_login.html", {"request": request})


@router.get("")
async def portal_dashboard(request: Request):
    """Member dashboard — profile, address, bank, teams."""
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

    # Serialize dates
    for key in ("geburtsdatum", "eintrittsdatum"):
        if member.get(key):
            member[key] = str(member[key])

    return templates.TemplateResponse("portal_dashboard.html", {
        "request": request,
        "member": member,
        "divisions": divisions,
        "teams": teams,
        "bank": bank,
        "is_admin": current["is_admin"],
    })
