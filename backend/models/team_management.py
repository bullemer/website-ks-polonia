"""
KS Polonia – Pydantic models for Team Management:
Mannschaftskasse (Team Treasury) and Team Tasks & Duties.
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import date, datetime


# --- Mannschaftskasse (Team Treasury) ---

class TeamTreasuryCreate(BaseModel):
    type: Literal["income", "expense", "fine"] = Field(
        ..., description="'income' (Einnahme), 'expense' (Ausgabe), 'fine' (Strafe)"
    )
    amount: float = Field(..., gt=0, description="Betrag in Euro")
    description: str = Field(..., min_length=2, max_length=255)
    member_id: Optional[int] = Field(None, description="Optional: Betroffenes Teammitglied (z.B. bei Strafe)")
    transaction_date: Optional[str] = Field(None, description="YYYY-MM-DD")


class TeamTreasuryResponse(BaseModel):
    id: int
    team_id: int
    member_id: Optional[int] = None
    member_name: Optional[str] = None
    type: str
    amount: float
    description: str
    transaction_date: Optional[str] = None
    created_by: Optional[int] = None
    created_at: Optional[str] = None


class TeamTreasurySummary(BaseModel):
    total_balance: float
    total_income: float
    total_expense: float
    total_fines: float
    transaction_count: int


# --- Team Tasks & Duties (Aufgaben & Dienste) ---

class TeamTaskCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = ""
    assigned_to: Optional[int] = Field(None, description="Member ID des zugewiesenen Spielers")
    due_date: Optional[str] = Field(None, description="YYYY-MM-DD")


class TeamTaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assigned_to: Optional[int] = None
    due_date: Optional[str] = None
    status: Optional[Literal["open", "completed"]] = None


class TeamTaskResponse(BaseModel):
    id: int
    team_id: int
    assigned_to: Optional[int] = None
    assigned_to_name: Optional[str] = None
    title: str
    description: Optional[str] = None
    due_date: Optional[str] = None
    status: str
    completed_at: Optional[str] = None
    created_by: Optional[int] = None
    created_at: Optional[str] = None


# --- Role & Member Management ---

class MemberRoleUpdate(BaseModel):
    role: Literal["superadmin", "admin", "member"]


# --- Team Website & Content Management ---

class TeamWebProfileUpdate(BaseModel):
    coach: Optional[str] = None
    contact_person: Optional[str] = None
    training_times: Optional[str] = None
    training_location: Optional[str] = None
    spielklasse: Optional[str] = None
    age_group: Optional[str] = None
    webpage_url: Optional[str] = None
    content: Optional[str] = None
    widget_id: Optional[str] = None
    external_url: Optional[str] = None


class TeamPhotoDelete(BaseModel):
    photo_src: str


# --- Team Announcements ---

class AnnouncementCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    content: str = Field("", max_length=2000)

class AnnouncementUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=255)
    content: Optional[str] = Field(None, max_length=2000)
    is_active: Optional[bool] = None


# --- News Articles ---

class NewsArticleCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=500)
    summary: str = Field("", max_length=1000)
    content: str = Field("", max_length=50000)
    category: str = Field("Allgemein")
    team_id: Optional[int] = None
    is_published: bool = False

class NewsArticleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=500)
    summary: Optional[str] = Field(None, max_length=1000)
    content: Optional[str] = Field(None, max_length=50000)
    category: Optional[str] = None
    cover_image: Optional[str] = None
    team_id: Optional[int] = None
    is_published: Optional[bool] = None

