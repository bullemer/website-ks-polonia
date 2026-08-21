"""
KS Polonia – Admin routes.
Full CRUD for members, divisions, teams, applications.
"""
import os
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Optional

from auth import require_admin
from models.member import MemberAdminUpdate
from models.division import DivisionCreate, DivisionUpdate, TeamCreate, TeamUpdate, TeamMemberAssign
from models.application import ApplicationReview
from services import member_service
from database import get_pool
from mailer import send_email
from config import SITE_URL

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "..", "templates"))

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard")
async def admin_dashboard(request: Request):
    admin = require_admin(request)
    stats = await member_service.get_dashboard_stats()
    return templates.TemplateResponse(request, "admin_dashboard.html", {
        "stats": stats, "admin": admin,
    })


@router.get("/dashboard/stats")
async def admin_dashboard_stats(request: Request):
    require_admin(request)
    return await member_service.get_dashboard_stats()


@router.get("/members")
async def admin_list_members(
    request: Request, search: str = "", division_id: Optional[int] = None,
    active: Optional[str] = None, page: int = 1,
):
    require_admin(request)
    limit = 50
    offset = (page - 1) * limit
    is_active = {"true": True, "false": False}.get(active)

    members, total = await member_service.list_members(
        search=search, division_id=division_id, is_active=is_active,
        limit=limit, offset=offset,
    )
    for m in members:
        if m.get("eintrittsdatum"):
            m["eintrittsdatum"] = str(m["eintrittsdatum"])

    pool = await get_pool()
    async with pool.acquire() as conn:
        div_rows = await conn.fetch(
            "SELECT id, name, icon FROM divisions WHERE is_active = TRUE ORDER BY sort_order"
        )
        divisions = [dict(r) for r in div_rows]

    return templates.TemplateResponse(request, "admin_members.html", {
        "members": members, "total": total,
        "page": page, "total_pages": max(1, (total + limit - 1) // limit),
        "search": search, "division_id": division_id,
        "active_filter": active or "", "divisions": divisions,
    })


@router.get("/members/{member_id}")
async def admin_get_member(request: Request, member_id: int):
    require_admin(request)
    member = await member_service.get_member_by_id(member_id)
    if not member:
        raise HTTPException(status_code=404)
    divisions = await member_service.get_member_divisions(member_id)
    teams = await member_service.get_member_teams(member_id)
    bank = await member_service.get_bank_account(member_id)
    for key in ("geburtsdatum", "eintrittsdatum", "created_at", "updated_at"):
        if member.get(key):
            member[key] = str(member[key])
    return templates.TemplateResponse(request, "admin_member_detail.html", {
        "member": member, "divisions": divisions,
        "teams": teams, "bank": bank,
    })


@router.put("/members/{member_id}")
async def admin_update_member(request: Request, member_id: int, updates: MemberAdminUpdate):
    require_admin(request)
    update_dict = updates.model_dump(exclude_none=True)
    for df in ("geburtsdatum", "eintrittsdatum"):
        if df in update_dict:
            from services.member_service import _parse_date
            update_dict[df] = _parse_date(update_dict[df])
    success = await member_service.update_member_profile(member_id, update_dict)
    if success:
        return JSONResponse({"success": True, "message": "Mitglied aktualisiert"})
    raise HTTPException(status_code=500)


@router.delete("/members/{member_id}")
async def admin_deactivate_member(request: Request, member_id: int):
    require_admin(request)
    await member_service.update_member_profile(member_id, {"is_active": False})
    return JSONResponse({"success": True, "message": "Mitglied deaktiviert"})


@router.put("/members/{member_id}/admin")
async def admin_toggle_admin(request: Request, member_id: int):
    require_admin(request)
    member = await member_service.get_member_by_id(member_id)
    if not member:
        raise HTTPException(status_code=404)
    new_status = not member["is_admin"]
    await member_service.update_member_profile(member_id, {"is_admin": new_status})
    return JSONResponse({"success": True, "is_admin": new_status})


# --- Divisions ---
@router.get("/divisions")
async def admin_list_divisions(request: Request):
    require_admin(request)
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT d.*,
                COUNT(DISTINCT md.member_id) FILTER (WHERE md.status = 'active') as member_count,
                COUNT(DISTINCT t.id) FILTER (WHERE t.is_active = TRUE) as team_count
            FROM divisions d
            LEFT JOIN member_divisions md ON md.division_id = d.id
            LEFT JOIN teams t ON t.division_id = d.id
            GROUP BY d.id ORDER BY d.sort_order
        """)
    return templates.TemplateResponse(request, "admin_divisions.html", {
        "divisions": [dict(r) for r in rows],
    })


@router.post("/divisions")
async def admin_create_division(request: Request, data: DivisionCreate):
    require_admin(request)
    pool = await get_pool()
    async with pool.acquire() as conn:
        new_id = await conn.fetchval(
            "INSERT INTO divisions (name, sport, icon, description, sort_order) VALUES ($1,$2,$3,$4,$5) RETURNING id",
            data.name, data.sport, data.icon or "⚽", data.description or "", data.sort_order or 0,
        )
    return JSONResponse({"success": True, "id": new_id})


@router.put("/divisions/{div_id}")
async def admin_update_division(request: Request, div_id: int, data: DivisionUpdate):
    require_admin(request)
    updates = data.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400)
    set_c = ", ".join(f"{k} = ${i+2}" for i, k in enumerate(updates.keys()))
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(f"UPDATE divisions SET {set_c} WHERE id = $1", div_id, *updates.values())
    return JSONResponse({"success": True})


# --- Teams ---
@router.get("/teams")
async def admin_list_teams(request: Request, division_id: Optional[int] = None):
    require_admin(request)
    pool = await get_pool()
    async with pool.acquire() as conn:
        q = """SELECT t.*, d.name as division_name,
               COUNT(mt.member_id) FILTER (WHERE mt.status = 'active') as member_count
               FROM teams t LEFT JOIN divisions d ON d.id = t.division_id
               LEFT JOIN member_teams mt ON mt.team_id = t.id"""
        if division_id:
            q += f" WHERE t.division_id = $1 GROUP BY t.id, d.name ORDER BY t.sort_order"
            rows = await conn.fetch(q, division_id)
        else:
            q += " GROUP BY t.id, d.name ORDER BY d.sort_order, t.sort_order"
            rows = await conn.fetch(q)
    return JSONResponse({"teams": [dict(r) for r in rows]})


@router.post("/teams")
async def admin_create_team(request: Request, data: TeamCreate):
    require_admin(request)
    pool = await get_pool()
    async with pool.acquire() as conn:
        new_id = await conn.fetchval(
            """INSERT INTO teams (division_id, mannschaftsart, mannschaftsname, spielklasse,
               coach, age_group, widget_id, sort_order) VALUES ($1,$2,$3,$4,$5,$6,$7,$8) RETURNING id""",
            data.division_id, data.mannschaftsart, data.mannschaftsname,
            data.spielklasse or "", data.coach or "", data.age_group or "",
            data.widget_id or "", data.sort_order or 0,
        )
    return JSONResponse({"success": True, "id": new_id})


@router.put("/teams/{team_id}")
async def admin_update_team(request: Request, team_id: int, data: TeamUpdate):
    require_admin(request)
    updates = data.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400)
    set_c = ", ".join(f"{k} = ${i+2}" for i, k in enumerate(updates.keys()))
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(f"UPDATE teams SET {set_c} WHERE id = $1", team_id, *updates.values())
    return JSONResponse({"success": True})


@router.post("/teams/{team_id}/members")
async def admin_assign_member(request: Request, team_id: int, data: TeamMemberAssign):
    require_admin(request)
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """INSERT INTO member_teams (member_id, team_id, position, jersey_number)
               VALUES ($1,$2,$3,$4) ON CONFLICT (member_id, team_id)
               DO UPDATE SET position=$3, jersey_number=$4, status='active', left_at=NULL""",
            data.member_id, team_id, data.position or "", data.jersey_number,
        )
    return JSONResponse({"success": True})


@router.delete("/teams/{team_id}/members/{member_id}")
async def admin_remove_member(request: Request, team_id: int, member_id: int):
    require_admin(request)
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE member_teams SET status='inactive', left_at=CURRENT_DATE WHERE member_id=$1 AND team_id=$2",
            member_id, team_id,
        )
    return JSONResponse({"success": True})


# --- Applications ---
@router.get("/applications")
async def admin_list_applications(request: Request):
    admin = require_admin(request)
    apps = await member_service.get_pending_applications()
    for a in apps:
        for k in ("submitted_at", "geburtsdatum"):
            if a.get(k):
                a[k] = str(a[k])
    return templates.TemplateResponse(request, "admin_applications.html", {
        "applications": apps, "admin": admin,
    })


@router.put("/applications/{app_id}")
async def admin_review_application(request: Request, app_id: int, data: ApplicationReview):
    admin = require_admin(request)
    if data.status == "approved":
        result = await member_service.approve_application(app_id, admin["email"], data.admin_notes or "")
        if not result:
            raise HTTPException(status_code=404)
        body = (
            f"Hallo {result['vorname']},\n\nWillkommen beim KS Polonia Hamburg e.V.!\n\n"
            f"Portal: {SITE_URL}/portal/login\nE-Mail: {result['email']}\n"
            f"Passwort: {result['temp_password']}\n\n"
            f"Bitte ändern Sie Ihr Passwort nach der ersten Anmeldung.\n\n"
            f"Sportliche Grüße,\nKS Polonia Hamburg e.V."
        )
        send_email(subject="Willkommen beim KS Polonia! – Zugangsdaten", text_body=body)
        return JSONResponse({"success": True, "message": f"Genehmigt. E-Mail an {result['email']} gesendet."})
    elif data.status == "rejected":
        ok = await member_service.reject_application(app_id, admin["email"], data.admin_notes or "")
        if not ok:
            raise HTTPException(status_code=404)
        return JSONResponse({"success": True, "message": "Abgelehnt"})
    raise HTTPException(status_code=400, detail="Status: 'approved' oder 'rejected'")


# --- Payments (admin) ---

@router.get("/members/{member_id}/payments")
async def admin_get_payments(request: Request, member_id: int):
    """Get all payments for a specific member."""
    require_admin(request)
    payments = await member_service.get_member_payments(member_id, limit=200)
    summary = await member_service.get_payment_summary(member_id)
    return {"payments": payments, "summary": summary}


@router.post("/members/{member_id}/payments")
async def admin_create_payment(request: Request, member_id: int):
    """Create a payment record for a member."""
    admin = require_admin(request)
    body = await request.json()

    amount = body.get("amount")
    if not amount or float(amount) <= 0:
        raise HTTPException(status_code=400, detail="Ungültiger Betrag")

    new_id = await member_service.create_payment(
        member_id=member_id,
        amount=float(amount),
        description=body.get("description", "Mitgliedsbeitrag"),
        period=body.get("period", ""),
        payment_date=body.get("payment_date", ""),
        payment_method=body.get("payment_method", "Überweisung"),
        status=body.get("status", "received"),
        notes=body.get("notes", ""),
        created_by=admin["email"],
    )
    return JSONResponse({"success": True, "id": new_id, "message": "Zahlung erfasst"})


@router.delete("/payments/{payment_id}")
async def admin_delete_payment(request: Request, payment_id: int):
    """Delete a payment record."""
    require_admin(request)
    ok = await member_service.delete_payment(payment_id)
    if not ok:
        raise HTTPException(status_code=404)
    return JSONResponse({"success": True, "message": "Zahlung gelöscht"})

