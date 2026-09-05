"""
KS Polonia – Team Management Service.
Handles team roster, Mannschaftskasse (treasury), and Team Tasks.
"""
import os
import json
import yaml
import datetime
from typing import Optional, List, Dict, Any
from database import get_pool

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _parse_date(date_str: Optional[str]) -> Optional[datetime.date]:
    if not date_str:
        return None
    try:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        try:
            return datetime.datetime.strptime(date_str, "%d.%m.%Y").date()
        except ValueError:
            return None


# ═══════════════════════════════════════
#  TEAM ROSTER & ADMIN PERMISSIONS
# ═══════════════════════════════════════

async def get_managed_teams(member_id: int, is_superadmin: bool = False) -> List[Dict[str, Any]]:
    """
    Get all teams a member has admin/trainer privileges for.
    If is_superadmin=True, returns all active teams in the club.
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        if is_superadmin:
            rows = await conn.fetch("""
                SELECT t.*, d.name as division_name, d.icon as division_icon,
                       COUNT(mt.member_id) FILTER (WHERE mt.status = 'active') as member_count
                FROM teams t
                LEFT JOIN divisions d ON d.id = t.division_id
                LEFT JOIN member_teams mt ON mt.team_id = t.id
                WHERE t.is_active = TRUE
                GROUP BY t.id, d.name, d.icon, d.sort_order
                ORDER BY d.sort_order, t.sort_order
            """)
        else:
            rows = await conn.fetch("""
                SELECT t.*, d.name as division_name, d.icon as division_icon,
                       mt_admin.role as admin_role,
                       COUNT(mt_all.member_id) FILTER (WHERE mt_all.status = 'active') as member_count
                FROM teams t
                JOIN member_teams mt_admin ON mt_admin.team_id = t.id 
                     AND mt_admin.member_id = $1 
                     AND mt_admin.status = 'active'
                LEFT JOIN divisions d ON d.id = t.division_id
                LEFT JOIN member_teams mt_all ON mt_all.team_id = t.id
                WHERE t.is_active = TRUE
                GROUP BY t.id, d.name, d.icon, d.sort_order, mt_admin.role
                ORDER BY d.sort_order, t.sort_order
            """, member_id)
        return [dict(r) for r in rows]


async def is_team_admin(member_id: int, team_id: int, is_superadmin: bool = False) -> bool:
    """Check if member can manage this team."""
    if is_superadmin:
        return True
    pool = await get_pool()
    async with pool.acquire() as conn:
        val = await conn.fetchval("""
            SELECT 1 FROM member_teams
            WHERE member_id = $1 AND team_id = $2 AND status = 'active'
        """, member_id, team_id)
        return bool(val)


async def get_team_members(team_id: int) -> List[Dict[str, Any]]:
    """Get all active members of a team with contact and player info."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT mt.id as assignment_id, mt.role, mt.position, mt.jersey_number, mt.status, mt.joined_at,
                   m.id as member_id, m.vorname, m.nachname, m.email, m.telefon, m.mitgliedsnummer,
                   m.membership_level, m.role as system_role
            FROM member_teams mt
            JOIN members m ON m.id = mt.member_id
            WHERE mt.team_id = $1 AND mt.status = 'active'
            ORDER BY
                CASE mt.role 
                    WHEN 'trainer' THEN 1 
                    WHEN 'co-trainer' THEN 2 
                    WHEN 'manager' THEN 3 
                    WHEN 'captain' THEN 4
                    ELSE 5 
                END,
                mt.jersey_number NULLS LAST,
                m.nachname, m.vorname
        """, team_id)
        res = []
        for r in rows:
            d = dict(r)
            if d.get("joined_at"):
                d["joined_at"] = str(d["joined_at"])
            res.append(d)
        return res


async def add_member_to_team(
    team_id: int,
    member_id: int,
    role: str = "player",
    position: str = "",
    jersey_number: Optional[int] = None,
) -> bool:
    """Add or reactivate a member in a team."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO member_teams (member_id, team_id, position, jersey_number, role, status, joined_at, left_at)
            VALUES ($1, $2, $3, $4, $5, 'active', CURRENT_DATE, NULL)
            ON CONFLICT (member_id, team_id)
            DO UPDATE SET 
                position = EXCLUDED.position,
                jersey_number = EXCLUDED.jersey_number,
                role = EXCLUDED.role,
                status = 'active',
                left_at = NULL
        """, member_id, team_id, position or "", jersey_number, role or "player")
        return True


async def remove_member_from_team(team_id: int, member_id: int) -> bool:
    """Remove a member from a team."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute("""
            DELETE FROM member_teams WHERE member_id = $1 AND team_id = $2
        """, member_id, team_id)
        return "DELETE 1" in result


# ═══════════════════════════════════════
#  MANNSCHAFTSKASSE (TEAM TREASURY)
# ═══════════════════════════════════════

async def get_team_treasury_summary(team_id: int) -> Dict[str, Any]:
    """Calculate current balance and summary of Mannschaftskasse."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT 
                COALESCE(SUM(CASE WHEN type IN ('income', 'fine') THEN amount ELSE 0 END), 0) as total_income_fines,
                COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) as total_expense,
                COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) as total_income,
                COALESCE(SUM(CASE WHEN type = 'fine' THEN amount ELSE 0 END), 0) as total_fines,
                COUNT(*) as transaction_count
            FROM team_treasury_transactions
            WHERE team_id = $1
        """, team_id)
        total_in = float(row["total_income_fines"])
        total_exp = float(row["total_expense"])
        return {
            "total_balance": round(total_in - total_exp, 2),
            "total_income": float(row["total_income"]),
            "total_expense": total_exp,
            "total_fines": float(row["total_fines"]),
            "transaction_count": row["transaction_count"],
        }


async def get_team_treasury_transactions(team_id: int, limit: int = 100) -> List[Dict[str, Any]]:
    """Get transaction history of Mannschaftskasse, newest first."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT t.id, t.team_id, t.member_id, t.type, t.amount, t.description,
                   t.transaction_date, t.created_by, t.created_at,
                   CONCAT(m.vorname, ' ', m.nachname) as member_name,
                   CONCAT(cb.vorname, ' ', cb.nachname) as created_by_name
            FROM team_treasury_transactions t
            LEFT JOIN members m ON m.id = t.member_id
            LEFT JOIN members cb ON cb.id = t.created_by
            WHERE t.team_id = $1
            ORDER BY t.transaction_date DESC, t.created_at DESC
            LIMIT $2
        """, team_id, limit)
        result = []
        for r in rows:
            d = dict(r)
            d["amount"] = float(d["amount"])
            if d.get("transaction_date"):
                d["transaction_date"] = str(d["transaction_date"])
            if d.get("created_at"):
                d["created_at"] = str(d["created_at"])
            result.append(d)
        return result


async def create_treasury_transaction(
    team_id: int,
    type_: str,
    amount: float,
    description: str,
    member_id: Optional[int] = None,
    transaction_date: Optional[str] = None,
    created_by: Optional[int] = None,
) -> int:
    """Record an income, expense, or fine in Mannschaftskasse."""
    pool = await get_pool()
    tx_date = _parse_date(transaction_date) if transaction_date else datetime.date.today()
    async with pool.acquire() as conn:
        new_id = await conn.fetchval("""
            INSERT INTO team_treasury_transactions (
                team_id, member_id, type, amount, description, transaction_date, created_by
            ) VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING id
        """, team_id, member_id, type_, amount, description, tx_date, created_by)
        return new_id


async def delete_treasury_transaction(transaction_id: int, team_id: int) -> bool:
    """Delete a transaction from Mannschaftskasse."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute("""
            DELETE FROM team_treasury_transactions WHERE id = $1 AND team_id = $2
        """, transaction_id, team_id)
        return "DELETE 1" in result


# ═══════════════════════════════════════
#  TEAM TASKS & DUTIES (AUFGABEN & DIENSTE)
# ═══════════════════════════════════════

async def get_team_tasks(team_id: int, assigned_to: Optional[int] = None) -> List[Dict[str, Any]]:
    """Get tasks for a team (optionally filtered by assigned member)."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        q = """
            SELECT t.id, t.team_id, t.assigned_to, t.title, t.description,
                   t.due_date, t.status, t.completed_at, t.created_by, t.created_at,
                   CONCAT(m.vorname, ' ', m.nachname) as assigned_to_name
            FROM team_tasks t
            LEFT JOIN members m ON m.id = t.assigned_to
            WHERE t.team_id = $1
        """
        params = [team_id]
        if assigned_to:
            q += " AND t.assigned_to = $2"
            params.append(assigned_to)
        q += " ORDER BY CASE WHEN t.status = 'open' THEN 1 ELSE 2 END, t.due_date ASC, t.created_at DESC"
        rows = await conn.fetch(q, *params)
        res = []
        for r in rows:
            d = dict(r)
            for k in ("due_date", "completed_at", "created_at"):
                if d.get(k):
                    d[k] = str(d[k])
            res.append(d)
        return res


async def create_team_task(
    team_id: int,
    title: str,
    description: str = "",
    assigned_to: Optional[int] = None,
    due_date: Optional[str] = None,
    created_by: Optional[int] = None,
) -> int:
    """Create a new team duty or task."""
    pool = await get_pool()
    d_date = _parse_date(due_date)
    async with pool.acquire() as conn:
        new_id = await conn.fetchval("""
            INSERT INTO team_tasks (team_id, assigned_to, title, description, due_date, status, created_by)
            VALUES ($1, $2, $3, $4, $5, 'open', $6)
            RETURNING id
        """, team_id, assigned_to, title, description or "", d_date, created_by)
        return new_id


async def update_team_task(task_id: int, team_id: int, updates: Dict[str, Any]) -> bool:
    """Update task details or status."""
    pool = await get_pool()
    if not updates:
        return True

    if "status" in updates and updates["status"] == "completed":
        updates["completed_at"] = datetime.datetime.now(datetime.timezone.utc)
    elif "status" in updates and updates["status"] == "open":
        updates["completed_at"] = None

    if "due_date" in updates and isinstance(updates["due_date"], str):
        updates["due_date"] = _parse_date(updates["due_date"])

    set_clauses = [f"{k} = ${i+3}" for i, k in enumerate(updates.keys())]
    async with pool.acquire() as conn:
        res = await conn.execute(
            f"UPDATE team_tasks SET {', '.join(set_clauses)} WHERE id = $1 AND team_id = $2",
            task_id, team_id, *updates.values()
        )
        return "UPDATE 1" in res


async def delete_team_task(task_id: int, team_id: int) -> bool:
    """Delete a team task."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        res = await conn.execute("DELETE FROM team_tasks WHERE id = $1 AND team_id = $2", task_id, team_id)
        return "DELETE 1" in res


# ═══════════════════════════════════════
#  TEAM WEBSITE & CONTENT SYNC
# ═══════════════════════════════════════

def _extract_frontmatter_and_body(text: str):
    """Safely extract YAML frontmatter and markdown body from a document."""
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        fm_lines = []
        body_start_idx = 1
        for idx, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                body_start_idx = idx + 1
                break
            fm_lines.append(line)
        fm_text = "\n".join(fm_lines)
        body_text = "\n".join(lines[body_start_idx:])
        try:
            fm = yaml.safe_load(fm_text) or {}
        except Exception:
            fm = {}
        return fm, body_text.strip()
    return {}, text.strip()


async def get_team_web_profile(team_id: int) -> Optional[Dict[str, Any]]:
    """Get full team details for web content management."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT t.*, d.name as division_name, d.icon as division_icon
            FROM teams t
            LEFT JOIN divisions d ON d.id = t.division_id
            WHERE t.id = $1
        """, team_id)
        if not row:
            return None
        data = dict(row)
        if isinstance(data.get("gallery"), str):
            try:
                data["gallery"] = json.loads(data["gallery"])
            except Exception:
                data["gallery"] = []
        elif data.get("gallery") is None:
            data["gallery"] = []
        return data


async def update_team_web_profile(team_id: int, updates: Dict[str, Any]) -> bool:
    """Update team web fields in database."""
    allowed = {
        "coach", "contact_person", "training_times", "training_location",
        "spielklasse", "age_group", "webpage_url", "content"
    }
    fields = {k: v for k, v in updates.items() if k in allowed and v is not None}
    if not fields:
        return True

    set_clauses = [f"{k} = ${i+2}" for i, k in enumerate(fields.keys())]
    pool = await get_pool()
    async with pool.acquire() as conn:
        res = await conn.execute(
            f"UPDATE teams SET {', '.join(set_clauses)} WHERE id = $1",
            team_id, *fields.values()
        )
        return "UPDATE 1" in res


async def add_team_photo(team_id: int, photo_url: str, caption: str = "") -> List[Dict[str, str]]:
    """Add a photo to the team gallery JSON in database."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        curr = await conn.fetchval("SELECT gallery FROM teams WHERE id = $1", team_id)
        gallery = []
        if isinstance(curr, str):
            try:
                gallery = json.loads(curr)
            except Exception:
                gallery = []
        elif isinstance(curr, list):
            gallery = curr

        gallery.append({"src": photo_url, "caption": caption.strip()})
        await conn.execute("UPDATE teams SET gallery = $1::jsonb WHERE id = $2", json.dumps(gallery), team_id)
        return gallery


async def remove_team_photo(team_id: int, photo_src: str) -> List[Dict[str, str]]:
    """Remove a photo by its src from the team gallery JSON in database."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        curr = await conn.fetchval("SELECT gallery FROM teams WHERE id = $1", team_id)
        gallery = []
        if isinstance(curr, str):
            try:
                gallery = json.loads(curr)
            except Exception:
                gallery = []
        elif isinstance(curr, list):
            gallery = curr

        gallery = [img for img in gallery if img.get("src") != photo_src]
        await conn.execute("UPDATE teams SET gallery = $1::jsonb WHERE id = $2", json.dumps(gallery), team_id)
        return gallery


async def sync_team_to_website(team_id: int) -> Dict[str, Any]:
    """
    Synchronize the team's data (coach, training_times, gallery, content)
    to its corresponding Astro Markdown / Markdoc file on disk.
    """
    team = await get_team_web_profile(team_id)
    if not team:
        return {"success": False, "error": "Team nicht gefunden"}

    target_files = []
    m_name = (team.get("mannschaftsname") or "").lower()
    w_url = (team.get("webpage_url") or "").lower()

    if team_id == 11 or "e-junioren" in w_url or "1.e" in m_name:
        target_files.append(os.path.join(_REPO_ROOT, "src", "content", "teams", "e-junioren.mdoc"))
    elif team_id == 12 or "u12" in w_url or "u12" in m_name or "u10" in w_url or "u10" in m_name:
        target_files.append(os.path.join(_REPO_ROOT, "src", "content", "pages", "basketball-jugend-u12", "index.mdoc"))
    elif team_id == 13 or "ue35" in w_url or "ü35" in m_name or "ue35" in m_name:
        target_files.append(os.path.join(_REPO_ROOT, "src", "content", "pages", "basketball-herren-ue35", "index.mdoc"))
    else:
        # Fallback check based on slug in webpage_url
        slug = w_url.strip("/").split("/")[-1]
        if slug:
            candidate = os.path.join(_REPO_ROOT, "src", "content", "teams", f"{slug}.mdoc")
            if os.path.exists(candidate):
                target_files.append(candidate)

    synced_paths = []
    for path in target_files:
        if not os.path.exists(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                old_text = f.read()

            fm, old_body = _extract_frontmatter_and_body(old_text)

            if team.get("coach"):
                fm["coach"] = team["coach"]
            if team.get("training_times"):
                fm["trainingTimes"] = team["training_times"]
            if team.get("gallery") is not None:
                fm["gallery"] = team["gallery"]
            if team.get("spielklasse"):
                fm["spielklasse"] = team["spielklasse"]
            if team.get("age_group"):
                fm["ageGroup"] = team["age_group"]

            body_text = team.get("content") if team.get("content") else old_body

            new_content = f"---\n{yaml.dump(fm, sort_keys=False, allow_unicode=True)}---\n\n{body_text}\n"
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_content)
            synced_paths.append(path)
        except Exception as e:
            return {"success": False, "error": f"Fehler beim Schreiben von {os.path.basename(path)}: {str(e)}"}

    return {
        "success": True,
        "team_id": team_id,
        "synced_files": [os.path.basename(p) for p in synced_paths],
    }

