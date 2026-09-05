"""
KS Polonia – Admin routes.
Full CRUD for members, divisions, teams, applications.
"""
import os
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse, Response
from fastapi.templating import Jinja2Templates
from typing import Optional

from auth import require_admin, require_superadmin, require_team_admin
from models.member import MemberAdminUpdate
from models.division import DivisionCreate, DivisionUpdate, TeamCreate, TeamUpdate, TeamMemberAssign
from models.application import ApplicationReview
from models.team_management import MemberRoleUpdate
from services import member_service, team_service
from database import get_pool
from mailer import send_email
from config import SITE_URL

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "..", "templates"))

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard")
async def admin_dashboard(request: Request):
    admin = require_admin(request)
    is_super = admin.get("role") == "superadmin"
    stats = await member_service.get_dashboard_stats()
    managed_teams = await team_service.get_managed_teams(admin["member_id"], is_superadmin=is_super)
    return templates.TemplateResponse(request, "admin_dashboard.html", {
        "stats": stats, "admin": admin, "is_superadmin": is_super, "managed_teams": managed_teams,
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
async def admin_delete_member(request: Request, member_id: int):
    """Permanently delete a member and all related data (Superadmin only)."""
    require_superadmin(request)
    pool = await get_pool()
    async with pool.acquire() as conn:
        # Check member exists
        exists = await conn.fetchval("SELECT id FROM members WHERE id = $1", member_id)
        if not exists:
            raise HTTPException(status_code=404, detail="Mitglied nicht gefunden")
        # Delete in order (cascading relations first)
        await conn.execute("DELETE FROM member_payments WHERE member_id = $1", member_id)
        await conn.execute("DELETE FROM member_teams WHERE member_id = $1", member_id)
        await conn.execute("DELETE FROM member_divisions WHERE member_id = $1", member_id)
        await conn.execute("DELETE FROM member_bank_accounts WHERE member_id = $1", member_id)
        await conn.execute("DELETE FROM members WHERE id = $1", member_id)
    return JSONResponse({"success": True, "message": "Mitglied endgültig gelöscht"})


@router.put("/members/{member_id}/role")
async def admin_change_role(request: Request, member_id: int, data: MemberRoleUpdate):
    """Change member system role: superadmin, admin, or member (Superadmin only)."""
    require_superadmin(request)
    success = await member_service.update_member_profile(member_id, {"role": data.role})
    if success:
        return JSONResponse({"success": True, "message": f"Rolle auf '{data.role}' geändert"})
    raise HTTPException(status_code=500, detail="Fehler beim Aktualisieren der Rolle")


@router.put("/members/{member_id}/admin")
async def admin_toggle_admin(request: Request, member_id: int):
    require_superadmin(request)
    member = await member_service.get_member_by_id(member_id)
    if not member:
        raise HTTPException(status_code=404)
    new_status = not member["is_admin"]
    new_role = "admin" if new_status else "member"
    await member_service.update_member_profile(member_id, {"role": new_role})
    return JSONResponse({"success": True, "is_admin": new_status, "role": new_role})


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
        teams = await conn.fetch("""
            SELECT t.*, COUNT(mt.member_id) FILTER (WHERE mt.status = 'active') as member_count
            FROM teams t LEFT JOIN member_teams mt ON mt.team_id = t.id
            GROUP BY t.id ORDER BY t.sort_order
        """)
    divisions = [dict(r) for r in rows]
    teams_list = [dict(t) for t in teams]
    # Group teams by division_id
    for d in divisions:
        d["teams"] = [t for t in teams_list if t.get("division_id") == d["id"]]
    return templates.TemplateResponse(request, "admin_divisions.html", {
        "divisions": divisions,
    })


@router.post("/divisions")
async def admin_create_division(request: Request, data: DivisionCreate):
    require_superadmin(request)
    pool = await get_pool()
    async with pool.acquire() as conn:
        new_id = await conn.fetchval(
            "INSERT INTO divisions (name, sport, icon, description, sort_order) VALUES ($1,$2,$3,$4,$5) RETURNING id",
            data.name, data.sport, data.icon or "⚽", data.description or "", data.sort_order or 0,
        )
    return JSONResponse({"success": True, "id": new_id})


@router.put("/divisions/{div_id}")
async def admin_update_division(request: Request, div_id: int, data: DivisionUpdate):
    require_superadmin(request)
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


@router.get("/teams/{team_id}")
async def admin_team_detail(request: Request, team_id: int):
    """Team detail page with roster, Mannschaftskasse, and tasks."""
    admin = await require_team_admin(request, team_id)
    pool = await get_pool()
    async with pool.acquire() as conn:
        team = await conn.fetchrow("""
            SELECT t.*, d.name as division_name, d.icon as division_icon
            FROM teams t LEFT JOIN divisions d ON d.id = t.division_id
            WHERE t.id = $1
        """, team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team nicht gefunden")

        # Get team members with their roles
        team_members = await conn.fetch("""
            SELECT mt.id as assignment_id, mt.role, mt.position, mt.jersey_number, mt.status,
                   m.id as member_id, m.vorname, m.nachname, m.email, m.mitgliedsnummer
            FROM member_teams mt
            JOIN members m ON m.id = mt.member_id
            WHERE mt.team_id = $1 AND mt.status = 'active'
            ORDER BY
                CASE mt.role WHEN 'trainer' THEN 1 WHEN 'co-trainer' THEN 2 WHEN 'manager' THEN 3 ELSE 4 END,
                mt.jersey_number NULLS LAST,
                m.nachname
        """, team_id)

        # Get all active members for the add-member dropdown
        all_members = await conn.fetch("""
            SELECT id, vorname, nachname, mitgliedsnummer FROM members
            WHERE is_active = TRUE ORDER BY nachname, vorname
        """)

        # Get all divisions for breadcrumb
        divisions = await conn.fetch("SELECT id, name, icon FROM divisions WHERE is_active = TRUE ORDER BY sort_order")

    # Fetch treasury and tasks
    treasury_summary = await team_service.get_team_treasury_summary(team_id)
    treasury_transactions = await team_service.get_team_treasury_transactions(team_id)
    team_tasks = await team_service.get_team_tasks(team_id)

    team_dict = dict(team)
    if isinstance(team_dict.get("gallery"), str):
        import json
        try:
            team_dict["gallery"] = json.loads(team_dict["gallery"])
        except Exception:
            team_dict["gallery"] = []
    elif team_dict.get("gallery") is None:
        team_dict["gallery"] = []

    return templates.TemplateResponse(request, "admin_team_detail.html", {
        "team": team_dict,
        "team_members": [dict(m) for m in team_members],
        "all_members": [dict(m) for m in all_members],
        "divisions": [dict(d) for d in divisions],
        "treasury_summary": treasury_summary,
        "treasury_transactions": treasury_transactions,
        "team_tasks": team_tasks,
        "admin": admin,
        "is_superadmin": (admin.get("role") == "superadmin"),
    })


@router.post("/teams")
async def admin_create_team(request: Request, data: TeamCreate):
    require_superadmin(request)
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
    await require_team_admin(request, team_id)
    updates = data.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400)
    set_c = ", ".join(f"{k} = ${i+2}" for i, k in enumerate(updates.keys()))
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(f"UPDATE teams SET {set_c} WHERE id = $1", team_id, *updates.values())
    return JSONResponse({"success": True})


@router.delete("/teams/{team_id}")
async def admin_delete_team(request: Request, team_id: int):
    """Permanently delete a team and all member assignments (Superadmin only)."""
    require_superadmin(request)
    pool = await get_pool()
    async with pool.acquire() as conn:
        exists = await conn.fetchval("SELECT id FROM teams WHERE id = $1", team_id)
        if not exists:
            raise HTTPException(status_code=404, detail="Team nicht gefunden")
        await conn.execute("DELETE FROM member_teams WHERE team_id = $1", team_id)
        await conn.execute("DELETE FROM teams WHERE id = $1", team_id)
    return JSONResponse({"success": True, "message": "Team gelöscht"})


@router.post("/teams/{team_id}/members")
async def admin_assign_member(request: Request, team_id: int, data: TeamMemberAssign):
    require_admin(request)
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """INSERT INTO member_teams (member_id, team_id, position, jersey_number, role)
               VALUES ($1,$2,$3,$4,$5) ON CONFLICT (member_id, team_id)
               DO UPDATE SET position=$3, jersey_number=$4, role=$5, status='active', left_at=NULL""",
            data.member_id, team_id, data.position or "", data.jersey_number, data.role or "player",
        )
    return JSONResponse({"success": True})


@router.delete("/teams/{team_id}/members/{member_id}")
async def admin_remove_member(request: Request, team_id: int, member_id: int):
    require_admin(request)
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "DELETE FROM member_teams WHERE member_id=$1 AND team_id=$2",
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


# --- Season Ticket Holder Delete ---

@router.delete("/ticket-holders/{holder_id}")
async def admin_delete_ticket_holder(request: Request, holder_id: int):
    """Permanently delete a season ticket holder and all their tickets."""
    require_admin(request)
    pool = await get_pool()
    async with pool.acquire() as conn:
        exists = await conn.fetchval("SELECT id FROM season_ticket_holders WHERE id = $1", holder_id)
        if not exists:
            raise HTTPException(status_code=404, detail="Dauerkarten-Inhaber nicht gefunden")
        await conn.execute("DELETE FROM season_tickets WHERE holder_id = $1", holder_id)
        await conn.execute("DELETE FROM season_ticket_holders WHERE id = $1", holder_id)
    return JSONResponse({"success": True, "message": "Dauerkarten-Inhaber gelöscht"})


# ═══════════════════════════════════════
#  MITGLIEDSBESCHEINIGUNG (PDF) - ADMIN
# ═══════════════════════════════════════

@router.get("/members/{member_id}/certificate/pdf")
async def admin_download_membership_certificate(request: Request, member_id: int, purpose: str = ""):
    """Generate and download official Mitgliedsbescheinigung as PDF for any member (Admin)."""
    require_admin(request)
    member = await member_service.get_member_by_id(member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Mitglied nicht gefunden")

    divisions = await member_service.get_member_divisions(member_id)
    from services.certificate_pdf import generate_membership_certificate
    pdf_bytes = generate_membership_certificate(
        member=member,
        divisions=divisions,
        purpose=purpose,
        paid_current_year=True,
    )

    nachname = member.get("nachname", "Mitglied").strip()
    vorname = member.get("vorname", "").strip()
    raw_name = f"Mitgliedsbescheinigung_{nachname}_{vorname}.pdf"
    clean_name = "".join(c for c in raw_name if c.isalnum() or c in "._-")

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="{clean_name}"',
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )
