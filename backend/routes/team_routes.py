"""
KS Polonia – Team Management Routes.
Endpoints for Team Roster, Mannschaftskasse (Treasury), and Team Tasks (Aufgaben & Dienste).
Accessible to Superadmins and assigned Team Admins (trainers/managers).
"""
import os
import re
import secrets
from fastapi import APIRouter, Request, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Optional

from auth import get_current_member, require_admin, require_superadmin, require_team_admin
from models.division import TeamMemberAssign
from models.team_management import (
    TeamTreasuryCreate,
    TeamTaskCreate,
    TeamTaskUpdate,
    TeamWebProfileUpdate,
    TeamPhotoDelete,
)
from services import team_service, member_service

router = APIRouter(prefix="/teams", tags=["teams"])


# ═══════════════════════════════════════
#  TEAMS OVERVIEW
# ═══════════════════════════════════════

@router.get("/my-teams")
async def get_my_teams(request: Request):
    """
    Get all teams managed by the current user.
    Superadmins see all active teams; Admins see their assigned teams.
    """
    member = get_current_member(request)
    is_super = member.get("role") == "superadmin"
    teams = await team_service.get_managed_teams(member["member_id"], is_superadmin=is_super)
    return {
        "is_superadmin": is_super,
        "teams": teams,
    }


# ═══════════════════════════════════════
#  ROSTER MANAGEMENT
# ═══════════════════════════════════════

@router.get("/{team_id}/roster")
async def get_team_roster(request: Request, team_id: int):
    """Get the active roster for a team."""
    # Any logged in member can view roster
    get_current_member(request)
    members = await team_service.get_team_members(team_id)
    return {"members": members}


@router.post("/{team_id}/members")
async def add_team_member(request: Request, team_id: int, data: TeamMemberAssign):
    """Add a member to the team (requires team admin or superadmin)."""
    await require_team_admin(request, team_id)
    success = await team_service.add_member_to_team(
        team_id=team_id,
        member_id=data.member_id,
        role=data.role or "player",
        position=data.position or "",
        jersey_number=data.jersey_number,
    )
    if success:
        return JSONResponse({"success": True, "message": "Mitglied zum Team hinzugefügt"})
    raise HTTPException(status_code=500, detail="Fehler beim Hinzufügen")


@router.delete("/{team_id}/members/{member_id}")
async def remove_team_member(request: Request, team_id: int, member_id: int):
    """Remove a member from the team (requires team admin or superadmin)."""
    await require_team_admin(request, team_id)
    success = await team_service.remove_member_from_team(team_id=team_id, member_id=member_id)
    if success:
        return JSONResponse({"success": True, "message": "Mitglied aus Team entfernt"})
    raise HTTPException(status_code=500, detail="Fehler beim Entfernen")


# ═══════════════════════════════════════
#  MANNSCHAFTSKASSE (TEAM TREASURY)
# ═══════════════════════════════════════

@router.get("/{team_id}/treasury")
async def get_team_treasury(request: Request, team_id: int):
    """
    Get treasury balance and transaction history.
    Accessible to team members and team admins.
    """
    member = get_current_member(request)
    summary = await team_service.get_team_treasury_summary(team_id)
    transactions = await team_service.get_team_treasury_transactions(team_id)
    is_admin = (member.get("role") == "superadmin") or await team_service.is_team_admin(
        member["member_id"], team_id
    )

    return {
        "summary": summary,
        "transactions": transactions,
        "can_manage": is_admin,
    }


@router.post("/{team_id}/treasury")
async def create_treasury_transaction(request: Request, team_id: int, data: TeamTreasuryCreate):
    """Book income, expense, or fine into Mannschaftskasse."""
    admin = await require_team_admin(request, team_id)
    tx_id = await team_service.create_treasury_transaction(
        team_id=team_id,
        type_=data.type,
        amount=data.amount,
        description=data.description,
        member_id=data.member_id,
        transaction_date=data.transaction_date,
        created_by=admin["member_id"],
    )
    return JSONResponse({"success": True, "id": tx_id, "message": "Buchung gespeichert"})


@router.delete("/{team_id}/treasury/{tx_id}")
async def delete_treasury_transaction(request: Request, team_id: int, tx_id: int):
    """Delete a transaction from Mannschaftskasse."""
    await require_team_admin(request, team_id)
    success = await team_service.delete_treasury_transaction(tx_id, team_id)
    if success:
        return JSONResponse({"success": True, "message": "Buchung gelöscht"})
    raise HTTPException(status_code=404, detail="Buchung nicht gefunden")


# ═══════════════════════════════════════
#  TEAM TASKS & DUTIES (AUFGABEN & DIENSTE)
# ═══════════════════════════════════════

@router.get("/{team_id}/tasks")
async def get_team_tasks(request: Request, team_id: int):
    """Get tasks for this team."""
    member = get_current_member(request)
    tasks = await team_service.get_team_tasks(team_id)
    is_admin = (member.get("role") == "superadmin") or await team_service.is_team_admin(
        member["member_id"], team_id
    )

    return {
        "tasks": tasks,
        "can_manage": is_admin,
        "current_member_id": member["member_id"],
    }


@router.post("/{team_id}/tasks")
async def create_team_task(request: Request, team_id: int, data: TeamTaskCreate):
    """Create a new team task / duty (Trikotwäsche, Kabinendienst, etc.)."""
    admin = await require_team_admin(request, team_id)
    task_id = await team_service.create_team_task(
        team_id=team_id,
        title=data.title,
        description=data.description or "",
        assigned_to=data.assigned_to,
        due_date=data.due_date,
        created_by=admin["member_id"],
    )
    return JSONResponse({"success": True, "id": task_id, "message": "Aufgabe angelegt"})


@router.put("/{team_id}/tasks/{task_id}")
async def update_team_task(request: Request, team_id: int, task_id: int, data: TeamTaskUpdate):
    """Update task details or toggle status."""
    member = get_current_member(request)
    is_admin = (member.get("role") == "superadmin") or await team_service.is_team_admin(
        member["member_id"], team_id
    )

    updates = data.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="Keine Änderungen übermittelt")

    # Regular members can only toggle status on tasks assigned to them
    if not is_admin:
        if set(updates.keys()) != {"status"}:
            raise HTTPException(status_code=403, detail="Nur Team-Admins können Aufgabendetails ändern")

    success = await team_service.update_team_task(task_id, team_id, updates)
    if success:
        return JSONResponse({"success": True, "message": "Aufgabe aktualisiert"})
    raise HTTPException(status_code=500, detail="Fehler beim Aktualisieren")


@router.delete("/{team_id}/tasks/{task_id}")
async def delete_team_task(request: Request, team_id: int, task_id: int):
    """Delete a team task."""
    await require_team_admin(request, team_id)
    success = await team_service.delete_team_task(task_id, team_id)
    if success:
        return JSONResponse({"success": True, "message": "Aufgabe gelöscht"})
    raise HTTPException(status_code=404, detail="Aufgabe nicht gefunden")


# ═══════════════════════════════════════
#  TEAM WEBSITE & CONTENT SYNC
# ═══════════════════════════════════════

@router.get("/{team_id}/web-profile")
async def get_team_web_profile(request: Request, team_id: int):
    """Get full team profile for website editing."""
    await require_team_admin(request, team_id)
    profile = await team_service.get_team_web_profile(team_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Team nicht gefunden")
    return profile


@router.put("/{team_id}/web-profile")
async def update_team_web_profile(request: Request, team_id: int, data: TeamWebProfileUpdate):
    """Update team website information (trainingszeiten, coaches, content, etc.) and sync to site."""
    await require_team_admin(request, team_id)
    updates = data.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="Keine Änderungen übermittelt")

    ok = await team_service.update_team_web_profile(team_id, updates)
    sync_res = await team_service.sync_team_to_website(team_id)
    if ok:
        return JSONResponse({
            "success": True,
            "message": "Teamseite gespeichert und mit Website synchronisiert",
            "sync": sync_res,
        })
    raise HTTPException(status_code=500, detail="Fehler beim Speichern")


@router.post("/{team_id}/photos")
async def upload_team_photo(
    request: Request,
    team_id: int,
    photo: UploadFile = File(...),
    caption: str = Form(""),
):
    """Upload a new photo for the team gallery and sync to site."""
    await require_team_admin(request, team_id)
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

    content = await photo.read()
    with open(file_path, "wb") as f:
        f.write(content)

    from config import UPLOAD_DIR
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


@router.delete("/{team_id}/photos")
async def delete_team_photo(request: Request, team_id: int, data: TeamPhotoDelete):
    """Delete a photo from the team gallery and sync to site."""
    await require_team_admin(request, team_id)
    gallery = await team_service.remove_team_photo(team_id, data.photo_src)
    await team_service.sync_team_to_website(team_id)
    return JSONResponse({
        "success": True,
        "message": "Foto aus der Galerie entfernt",
        "gallery": gallery,
    })


@router.post("/{team_id}/sync-website")
async def sync_team_website(request: Request, team_id: int):
    """Manually trigger website sync for a team."""
    await require_team_admin(request, team_id)
    sync_res = await team_service.sync_team_to_website(team_id)
    return JSONResponse(sync_res)


@router.get("/{team_id}/public-info")
async def get_team_public_info(team_id: int):
    """Public endpoint for website frontends to fetch live team info."""
    profile = await team_service.get_team_web_profile(team_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Team nicht gefunden")
    safe_fields = {
        "id", "mannschaftsname", "mannschaftsart", "spielklasse", "coach",
        "contact_person", "training_times", "training_location", "webpage_url",
        "content", "gallery", "division_name", "division_icon"
    }
    return {k: v for k, v in profile.items() if k in safe_fields}

