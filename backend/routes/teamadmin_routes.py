"""
KS Polonia – Teamadmin (Teamoffizieller) Portal Routes.
Dedicated portal for team officials (trainers, managers, teamoffizielle)
who have role='member' in the system but team-level admin roles in member_teams.
"""
import os
import re
import secrets
import datetime
import json
from typing import Optional

from fastapi import APIRouter, Request, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from auth import get_current_member
from models.team_management import TeamWebProfileUpdate, TeamPhotoDelete, AnnouncementCreate, AnnouncementUpdate
from services import member_service, team_service
from database import get_pool
from config import UPLOAD_DIR

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "..", "templates"))

router = APIRouter(prefix="/teamadmin", tags=["teamadmin"])


# ═══════════════════════════════════════
#  Pydantic models
# ═══════════════════════════════════════

class PaymentCreate(BaseModel):
    description: str
    amount: float
    period: str = ""
    payment_method: str = ""
    status: str = "offen"
    notes: str = ""


class TeamMemberUpdate(BaseModel):
    role: Optional[str] = None
    position: Optional[str] = None
    jersey_number: Optional[int] = None


class AddMemberRequest(BaseModel):
    member_id: int
    role: str = "player"
    position: str = ""
    jersey_number: Optional[int] = None


# ═══════════════════════════════════════
#  Auth helpers
# ═══════════════════════════════════════

TEAM_ADMIN_ROLES = ('trainer', 'manager', 'teamoffizieller')


async def _get_team_admin_teams(member_id: int) -> list[dict]:
    """Return list of team_ids where the member has a team-admin role."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT mt.team_id, t.mannschaftsname, t.mannschaftsart, t.spielklasse,
                   d.name as division_name, d.icon as division_icon,
                   mt.role as team_role,
                   COUNT(mt2.member_id) FILTER (WHERE mt2.status = 'active') as member_count
            FROM member_teams mt
            JOIN teams t ON t.id = mt.team_id
            LEFT JOIN divisions d ON d.id = t.division_id
            LEFT JOIN member_teams mt2 ON mt2.team_id = t.id
            WHERE mt.member_id = $1
              AND mt.role IN ('trainer', 'manager', 'teamoffizieller')
              AND mt.status = 'active'
              AND t.is_active = TRUE
            GROUP BY mt.team_id, t.mannschaftsname, t.mannschaftsart, t.spielklasse,
                     d.name, d.icon, mt.role
            ORDER BY d.name, t.mannschaftsname
            """,
            member_id,
        )
    return [dict(r) for r in rows]


async def _require_my_team(request: Request, team_id: int) -> dict:
    """
    Ensure the current user is a team admin for the given team,
    or a system-level admin/superadmin.
    Returns the member dict or raises 403.
    """
    member = get_current_member(request)

    # System-level superadmin/admin can manage any team
    if member.get("role") in ("superadmin", "admin"):
        return member

    # Check team-level role
    pool = await get_pool()
    async with pool.acquire() as conn:
        team_role = await conn.fetchval(
            """
            SELECT role FROM member_teams
            WHERE member_id = $1 AND team_id = $2 AND status = 'active'
            """,
            member["member_id"], team_id,
        )
        if team_role and team_role in TEAM_ADMIN_ROLES:
            return member

    raise HTTPException(status_code=403, detail="Keine Berechtigung für dieses Team")


# ═══════════════════════════════════════
#  1. Dashboard
# ═══════════════════════════════════════

@router.get("/")
@router.get("")
async def teamadmin_dashboard(request: Request):
    """Dashboard showing all teams the current user manages."""
    member = get_current_member(request)
    teams = await _get_team_admin_teams(member["member_id"])
    return templates.TemplateResponse(request, "teamadmin_dashboard.html", {
        "teams": teams,
        "sidebar_teams": teams,
        "member": member,
        "no_teams": len(teams) == 0,
        "message": "Keine Teams zugewiesen" if not teams else "",
    })


# ═══════════════════════════════════════
#  2. Team Detail
# ═══════════════════════════════════════

@router.get("/team/{team_id}")
async def teamadmin_team_detail(request: Request, team_id: int):
    """Team detail page with roster and treasury summary."""
    member = await _require_my_team(request, team_id)
    sidebar_teams = await _get_team_admin_teams(member["member_id"])
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
                   m.id as member_id, m.vorname, m.nachname, m.email, m.mitgliedsnummer,
                   m.claim_token, m.telefon
            FROM member_teams mt
            JOIN members m ON m.id = mt.member_id
            WHERE mt.team_id = $1 AND mt.status = 'active'
            ORDER BY
                CASE mt.role WHEN 'trainer' THEN 1 WHEN 'co-trainer' THEN 2 WHEN 'teamoffizieller' THEN 3 WHEN 'manager' THEN 4 ELSE 5 END,
                mt.jersey_number NULLS LAST,
                m.nachname
        """, team_id)

        # All active members for add-member dropdown
        all_members = await conn.fetch("""
            SELECT id, vorname, nachname, mitgliedsnummer FROM members
            WHERE is_active = TRUE ORDER BY nachname, vorname
        """)

    # Treasury summary
    treasury_summary = await team_service.get_team_treasury_summary(team_id)

    team_dict = dict(team)
    if isinstance(team_dict.get("gallery"), str):
        try:
            team_dict["gallery"] = json.loads(team_dict["gallery"])
        except Exception:
            team_dict["gallery"] = []
    elif team_dict.get("gallery") is None:
        team_dict["gallery"] = []

    return templates.TemplateResponse(request, "teamadmin_team.html", {
        "team": team_dict,
        "team_members": [dict(m) for m in team_members],
        "all_members": [dict(m) for m in all_members],
        "treasury_summary": treasury_summary,
        "sidebar_teams": sidebar_teams,
        "member": member,
    })


# ═══════════════════════════════════════
#  3. Beiträge Matrix
# ═══════════════════════════════════════

@router.get("/team/{team_id}/beitraege")
async def teamadmin_beitraege(request: Request, team_id: int, year: Optional[int] = None):
    """Monthly payment overview matrix scoped to this team."""
    member = await _require_my_team(request, team_id)
    sidebar_teams = await _get_team_admin_teams(member["member_id"])
    current_year = datetime.datetime.now().year
    selected_year = year or current_year

    # Force team_id filter — team admins only see their own team
    matrix = await member_service.get_beitraege_matrix(selected_year, division_id=None, team_id=team_id)

    pool = await get_pool()
    async with pool.acquire() as conn:
        team = await conn.fetchrow("""
            SELECT t.id, t.mannschaftsname, d.name as division_name, d.icon as division_icon
            FROM teams t LEFT JOIN divisions d ON d.id = t.division_id
            WHERE t.id = $1
        """, team_id)

    current_month = datetime.datetime.now().month if selected_year == current_year else 12
    month_names = ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez']

    return templates.TemplateResponse(request, "teamadmin_beitraege.html", {
        "matrix": matrix,
        "year": selected_year,
        "current_year": current_year,
        "current_month": current_month,
        "month_names": month_names,
        "team_id": team_id,
        "team": dict(team) if team else {"id": team_id},
        "sidebar_teams": sidebar_teams,
        "member": member,
    })


# ═══════════════════════════════════════
#  4. Add Payment
# ═══════════════════════════════════════

@router.post("/team/{team_id}/payments/{member_id}")
async def teamadmin_create_payment(request: Request, team_id: int, member_id: int, data: PaymentCreate):
    """Create a payment record for a member in this team."""
    admin = await _require_my_team(request, team_id)

    # Verify member belongs to this team
    pool = await get_pool()
    async with pool.acquire() as conn:
        in_team = await conn.fetchval(
            "SELECT 1 FROM member_teams WHERE member_id = $1 AND team_id = $2 AND status = 'active'",
            member_id, team_id,
        )
    if not in_team:
        raise HTTPException(status_code=403, detail="Mitglied gehört nicht zu diesem Team")

    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="Ungültiger Betrag")

    new_id = await member_service.create_payment(
        member_id=member_id,
        amount=data.amount,
        description=data.description,
        period=data.period,
        payment_date="",
        payment_method=data.payment_method,
        status=data.status,
        notes=data.notes,
        created_by=admin["email"],
    )
    return JSONResponse({"success": True, "id": new_id, "message": "Zahlung erfasst"})


# ═══════════════════════════════════════
#  5. Delete Payment
# ═══════════════════════════════════════

@router.delete("/team/{team_id}/payments/{member_id}/{payment_id}")
async def teamadmin_delete_payment(request: Request, team_id: int, member_id: int, payment_id: int):
    """Delete a payment record, verifying member belongs to team and payment belongs to member."""
    await _require_my_team(request, team_id)

    pool = await get_pool()
    async with pool.acquire() as conn:
        # Verify member belongs to team
        in_team = await conn.fetchval(
            "SELECT 1 FROM member_teams WHERE member_id = $1 AND team_id = $2 AND status = 'active'",
            member_id, team_id,
        )
        if not in_team:
            raise HTTPException(status_code=403, detail="Mitglied gehört nicht zu diesem Team")

        # Verify payment belongs to member
        owner = await conn.fetchval(
            "SELECT member_id FROM member_payments WHERE id = $1", payment_id
        )
        if owner is None:
            raise HTTPException(status_code=404, detail="Zahlung nicht gefunden")
        if owner != member_id:
            raise HTTPException(status_code=403, detail="Zahlung gehört nicht zu diesem Mitglied")

    ok = await member_service.delete_payment(payment_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Zahlung nicht gefunden")
    return JSONResponse({"success": True, "message": "Zahlung gelöscht"})


# ═══════════════════════════════════════
#  6. Team Page Editor
# ═══════════════════════════════════════

@router.get("/team/{team_id}/page")
async def teamadmin_page_editor(request: Request, team_id: int):
    """Render team web profile editor."""
    member = await _require_my_team(request, team_id)
    sidebar_teams = await _get_team_admin_teams(member["member_id"])
    profile = await team_service.get_team_web_profile(team_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Team nicht gefunden")
    return templates.TemplateResponse(request, "teamadmin_page_editor.html", {
        "team": profile,
        "team_id": team_id,
        "tid": team_id,
        "sidebar_teams": sidebar_teams,
        "member": member,
    })


# ═══════════════════════════════════════
#  7. Save Team Page
# ═══════════════════════════════════════

@router.put("/team/{team_id}/page")
async def teamadmin_save_page(request: Request, team_id: int, data: TeamWebProfileUpdate):
    """Update team web profile and sync to website."""
    await _require_my_team(request, team_id)
    updates = data.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="Keine Änderungen übermittelt")
    await team_service.update_team_web_profile(team_id, updates)
    await team_service.sync_team_to_website(team_id)
    return JSONResponse({"success": True, "message": "Teamseite aktualisiert und synchronisiert"})


# ═══════════════════════════════════════
#  8. Upload Photo
# ═══════════════════════════════════════

@router.post("/team/{team_id}/photos")
async def teamadmin_upload_photo(
    request: Request,
    team_id: int,
    photo: UploadFile = File(...),
    caption: str = Form(""),
):
    """Upload a new photo for the team gallery and sync to site."""
    await _require_my_team(request, team_id)
    if not photo.filename:
        raise HTTPException(status_code=400, detail="Keine Datei ausgewählt")

    ext = os.path.splitext(photo.filename)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".webp", ".gif"]:
        raise HTTPException(status_code=400, detail="Nur Bilddateien (JPG, PNG, WebP) erlaubt")

    safe_name = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", photo.filename)
    unique_filename = f"team_{team_id}_{secrets.token_hex(4)}_{safe_name}"

    public_teams_dir = os.path.join(team_service._REPO_ROOT, "public", "images", "teams")
    os.makedirs(public_teams_dir, exist_ok=True)
    file_path = os.path.join(public_teams_dir, unique_filename)

    # Read in chunks with 5MB limit
    MAX_PHOTO_SIZE = 5 * 1024 * 1024
    chunks = []
    total = 0
    while True:
        chunk = await photo.read(8192)
        if not chunk:
            break
        total += len(chunk)
        if total > MAX_PHOTO_SIZE:
            raise HTTPException(status_code=400, detail="Datei zu groß. Maximale Größe: 5 MB")
        chunks.append(chunk)
    content = b"".join(chunks)
    with open(file_path, "wb") as f:
        f.write(content)

    if os.path.exists(UPLOAD_DIR):
        try:
            hetzner_dir = os.path.join(UPLOAD_DIR, "teams")
            os.makedirs(hetzner_dir, exist_ok=True)
            with open(os.path.join(hetzner_dir, unique_filename), "wb") as f:
                f.write(content)
        except Exception:
            pass

    photo_url = f"/images/teams/{unique_filename}"
    gallery = await team_service.add_team_photo(team_id, photo_url, caption)
    await team_service.sync_team_to_website(team_id)

    return JSONResponse({
        "success": True,
        "message": "Foto erfolgreich hochgeladen und Galerie aktualisiert",
        "photo_url": photo_url,
        "gallery": gallery,
    })


# ═══════════════════════════════════════
#  9. Delete Photo
# ═══════════════════════════════════════

@router.delete("/team/{team_id}/photos")
async def teamadmin_delete_photo(request: Request, team_id: int, data: TeamPhotoDelete):
    """Delete a photo from the team gallery and sync to site."""
    await _require_my_team(request, team_id)
    gallery = await team_service.remove_team_photo(team_id, data.photo_src)
    await team_service.sync_team_to_website(team_id)
    return JSONResponse({
        "success": True,
        "message": "Foto aus der Galerie entfernt",
        "gallery": gallery,
    })


# ═══════════════════════════════════════
#  10. Update Member in Team
# ═══════════════════════════════════════

@router.put("/team/{team_id}/members/{member_id}")
async def teamadmin_update_member(request: Request, team_id: int, member_id: int, data: TeamMemberUpdate):
    """Update a team member's role, position, or jersey number."""
    await _require_my_team(request, team_id)
    updates = data.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="Keine Änderungen übermittelt")

    # Build dynamic SET clause with whitelist
    allowed = {"role", "position", "jersey_number"}
    unknown = set(updates.keys()) - allowed
    if unknown:
        raise HTTPException(status_code=400, detail=f"Unbekannte Felder: {', '.join(unknown)}")

    set_clause = ", ".join(f"{k} = ${i+3}" for i, k in enumerate(updates.keys()))
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute(
            f"UPDATE member_teams SET {set_clause} WHERE member_id = $1 AND team_id = $2 AND status = 'active'",
            member_id, team_id, *updates.values(),
        )
    if "UPDATE 0" in result:
        raise HTTPException(status_code=404, detail="Mitglied nicht in diesem Team gefunden")
    return JSONResponse({"success": True, "message": "Mitglied aktualisiert"})


# ═══════════════════════════════════════
#  11. Add Member to Team
# ═══════════════════════════════════════

@router.post("/team/{team_id}/members")
async def teamadmin_add_member(request: Request, team_id: int, data: AddMemberRequest):
    """Add a member to this team."""
    await _require_my_team(request, team_id)
    await team_service.add_member_to_team(
        team_id=team_id,
        member_id=data.member_id,
        role=data.role,
        position=data.position,
        jersey_number=data.jersey_number,
    )
    return JSONResponse({"success": True, "message": "Mitglied zum Team hinzugefügt"})


# ═══════════════════════════════════════
#  12. Remove Member from Team
# ═══════════════════════════════════════

@router.delete("/team/{team_id}/members/{member_id}")
async def teamadmin_remove_member(request: Request, team_id: int, member_id: int):
    """Remove a member from this team."""
    await _require_my_team(request, team_id)
    ok = await team_service.remove_member_from_team(team_id, member_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Mitglied nicht in diesem Team gefunden")
    return JSONResponse({"success": True, "message": "Mitglied aus dem Team entfernt"})



# ═══════════════════════════════════════
#  13. Team Announcements CRUD
# ═══════════════════════════════════════

@router.get("/team/{team_id}/announcements")
async def teamadmin_get_announcements(request: Request, team_id: int):
    """Get all announcements for a team (admin view)."""
    await _require_my_team(request, team_id)
    items = await team_service.get_team_announcements(team_id, active_only=False)
    return JSONResponse({"success": True, "announcements": [
        {
            "id": a["id"],
            "title": a["title"],
            "content": a["content"],
            "is_active": a["is_active"],
            "created_by_name": f"{a.get('vorname', '')} {a.get('nachname', '')}".strip() if a.get("nachname") else None,
            "created_at": a["created_at"].isoformat() if a.get("created_at") else None,
            "updated_at": a["updated_at"].isoformat() if a.get("updated_at") else None,
        }
        for a in items
    ]})


@router.post("/team/{team_id}/announcements")
async def teamadmin_create_announcement(request: Request, team_id: int, data: AnnouncementCreate):
    """Create a new announcement."""
    member = await _require_my_team(request, team_id)
    item = await team_service.create_announcement(team_id, data.title, data.content, member["member_id"])
    return JSONResponse({"success": True, "id": item["id"], "message": "Meldung erstellt"})


@router.put("/team/{team_id}/announcements/{ann_id}")
async def teamadmin_update_announcement(request: Request, team_id: int, ann_id: int, data: AnnouncementUpdate):
    """Update an announcement."""
    await _require_my_team(request, team_id)
    updates = data.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="Keine Änderungen übermittelt")
    ok = await team_service.update_announcement(ann_id, updates)
    if not ok:
        raise HTTPException(status_code=404, detail="Meldung nicht gefunden")
    return JSONResponse({"success": True, "message": "Meldung aktualisiert"})


@router.delete("/team/{team_id}/announcements/{ann_id}")
async def teamadmin_delete_announcement(request: Request, team_id: int, ann_id: int):
    """Delete an announcement."""
    await _require_my_team(request, team_id)
    ok = await team_service.delete_announcement(ann_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Meldung nicht gefunden")
    return JSONResponse({"success": True, "message": "Meldung gelöscht"})
