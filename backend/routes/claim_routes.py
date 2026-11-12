"""
KS Polonia – Claim routes.
Allows players/parents to self-register their contact details
(email + phone) via a unique claim link.
"""
import os
from datetime import date
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr
from typing import Optional

from auth import hash_password
from database import get_pool

router = APIRouter(prefix="/claim", tags=["claim"])

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "..", "templates"))


class ClaimRequest(BaseModel):
    email: EmailStr
    telefon: Optional[str] = None
    password: Optional[str] = None


def _format_date(d) -> str:
    """Format a date for display (DD.MM.YYYY)."""
    if isinstance(d, date):
        return d.strftime("%d.%m.%Y")
    if isinstance(d, str):
        try:
            return date.fromisoformat(d).strftime("%d.%m.%Y")
        except ValueError:
            return d
    return str(d) if d else ""


@router.get("/{token}")
async def claim_form(request: Request, token: str):
    """Show the claim form for a player identified by their token."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        member = await conn.fetchrow(
            "SELECT id, vorname, nachname, geburtsdatum, email, claim_token "
            "FROM members WHERE claim_token = $1 AND is_active = TRUE",
            token,
        )

    if not member:
        return templates.TemplateResponse(request, "claim.html", {
            "error": "Dieser Link ist ungültig oder wurde bereits verwendet.",
            "member": None,
            "team_name": None,
            "token": token,
            "already_claimed": False,
        })

    member_dict = dict(member)
    member_dict["geburtsdatum_display"] = _format_date(member.get("geburtsdatum"))

    # Check if already claimed (email already set)
    already_claimed = bool(member["email"])

    # Get team name
    team_name = None
    pool = await get_pool()
    async with pool.acquire() as conn:
        team = await conn.fetchrow(
            "SELECT t.mannschaftsname FROM teams t "
            "JOIN member_teams mt ON mt.team_id = t.id "
            "WHERE mt.member_id = $1 AND t.is_active = TRUE "
            "ORDER BY mt.created_at DESC LIMIT 1",
            member["id"],
        )
        if team:
            team_name = team["mannschaftsname"]

    return templates.TemplateResponse(request, "claim.html", {
        "error": None,
        "member": member_dict,
        "team_name": team_name,
        "token": token,
        "already_claimed": already_claimed,
    })


@router.post("/{token}")
async def claim_submit(token: str, req: ClaimRequest):
    """Process the claim form submission — save email, phone, optional password."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        member = await conn.fetchrow(
            "SELECT id, email, claim_token FROM members "
            "WHERE claim_token = $1 AND is_active = TRUE",
            token,
        )

    if not member:
        raise HTTPException(status_code=400, detail="Ungültiger oder bereits verwendeter Link.")

    if member["email"]:
        raise HTTPException(status_code=400, detail="Kontaktdaten wurden bereits hinterlegt.")

    # Check email not already used by another member
    async with pool.acquire() as conn:
        existing = await conn.fetchrow(
            "SELECT id FROM members WHERE email = $1 AND id != $2",
            req.email, member["id"],
        )
        if existing:
            raise HTTPException(
                status_code=409,
                detail="Diese E-Mail-Adresse ist bereits einem anderen Mitglied zugeordnet.",
            )

    # Build update
    has_password = False
    async with pool.acquire() as conn:
        if req.password and len(req.password) >= 8:
            hashed = hash_password(req.password)
            await conn.execute(
                """
                UPDATE members
                SET email = $1, telefon = $2, password_hash = $3,
                    claim_token = NULL, updated_at = NOW()
                WHERE id = $4
                """,
                req.email, req.telefon, hashed, member["id"],
            )
            has_password = True
        else:
            await conn.execute(
                """
                UPDATE members
                SET email = $1, telefon = $2,
                    claim_token = NULL, updated_at = NOW()
                WHERE id = $3
                """,
                req.email, req.telefon, member["id"],
            )

    return JSONResponse({
        "success": True,
        "message": "Kontaktdaten gespeichert",
        "has_password": has_password,
    })
