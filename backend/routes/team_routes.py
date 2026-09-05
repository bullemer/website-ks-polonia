"""
KS Polonia – Team Management Routes.
Endpoints for Team Roster, Mannschaftskasse (Treasury), and Team Tasks (Aufgaben & Dienste).
Accessible to Superadmins and assigned Team Admins (trainers/managers).
"""
import os
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional

from auth import get_current_member, require_admin, require_superadmin, require_team_admin
from models.division import TeamMemberAssign
from models.team_management import (
    TeamTreasuryCreate,
    TeamTaskCreate,
    TeamTaskUpdate,
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
