"""
Pydantic models for Divisions and Teams.
"""
from pydantic import BaseModel
from typing import Optional


# --- Division models ---

class DivisionCreate(BaseModel):
    name: str
    sport: str
    icon: Optional[str] = "⚽"
    description: Optional[str] = ""
    sort_order: Optional[int] = 0


class DivisionUpdate(BaseModel):
    name: Optional[str] = None
    sport: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class DivisionResponse(BaseModel):
    id: int
    name: str
    sport: str
    icon: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True
    sort_order: int = 0
    member_count: Optional[int] = 0
    team_count: Optional[int] = 0

    class Config:
        from_attributes = True


# --- Team models ---

class TeamCreate(BaseModel):
    division_id: int
    mannschaftsart: str
    mannschaftsname: str
    spielklasse: Optional[str] = ""
    coach: Optional[str] = ""
    age_group: Optional[str] = ""
    widget_id: Optional[str] = ""
    sort_order: Optional[int] = 0


class TeamUpdate(BaseModel):
    division_id: Optional[int] = None
    mannschaftsart: Optional[str] = None
    mannschaftsname: Optional[str] = None
    spielklasse: Optional[str] = None
    coach: Optional[str] = None
    age_group: Optional[str] = None
    widget_id: Optional[str] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class TeamResponse(BaseModel):
    id: int
    division_id: Optional[int] = None
    division_name: Optional[str] = None
    mannschaftsart: str
    mannschaftsname: str
    spielklasse: Optional[str] = None
    coach: Optional[str] = None
    age_group: Optional[str] = None
    widget_id: Optional[str] = None
    is_active: bool = True
    sort_order: int = 0
    member_count: Optional[int] = 0

    class Config:
        from_attributes = True


class TeamMemberAssign(BaseModel):
    """Assign a member to a team."""
    member_id: int
    position: Optional[str] = ""
    jersey_number: Optional[int] = None
    role: Optional[str] = "player"  # player, trainer, co-trainer, manager
