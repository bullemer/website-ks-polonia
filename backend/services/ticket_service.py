"""
KS Polonia – Season Ticket business logic.
Handles ticket holder registration, ticket application, and admin approval.
"""
import datetime
import secrets
from database import get_pool
from auth import hash_password, generate_token


CURRENT_SEASON = "2026/2027"


async def generate_ticket_code(season: str) -> str:
    """Generate next ticket code: DK-YYYY-NNNN."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        seq = await conn.fetchval("SELECT nextval('season_ticket_seq')")
        year = season.split("/")[0] if "/" in season else str(datetime.datetime.now().year)
        return f"DK-{year}-{seq:04d}"


async def create_holder_and_apply(
    vorname: str,
    nachname: str,
    email: str,
    telefon: str = "",
    season: str = "",
) -> dict:
    """
    Register a new season ticket holder and create a pending ticket application.
    If the holder already exists, just create a new ticket for the season.
    """
    pool = await get_pool()
    season = season or CURRENT_SEASON

    async with pool.acquire() as conn:
        # Check if holder already exists
        existing = await conn.fetchrow(
            "SELECT id FROM season_ticket_holders WHERE email = $1", email
        )

        if existing:
            holder_id = existing["id"]
            # Update name/phone if changed
            await conn.execute(
                "UPDATE season_ticket_holders SET vorname=$1, nachname=$2, telefon=$3, updated_at=NOW() WHERE id=$4",
                vorname, nachname, telefon or "", holder_id,
            )
        else:
            holder_id = await conn.fetchval(
                """
                INSERT INTO season_ticket_holders (vorname, nachname, email, telefon)
                VALUES ($1, $2, $3, $4)
                RETURNING id
                """,
                vorname, nachname, email, telefon or "",
            )

        # Check if ticket for this season already exists
        existing_ticket = await conn.fetchrow(
            "SELECT id, status FROM season_tickets WHERE holder_id = $1 AND season = $2",
            holder_id, season,
        )
        if existing_ticket:
            return {
                "holder_id": holder_id,
                "ticket_id": existing_ticket["id"],
                "status": existing_ticket["status"],
                "already_exists": True,
            }

        # Create pending ticket
        ticket_id = await conn.fetchval(
            """
            INSERT INTO season_tickets (holder_id, season, status)
            VALUES ($1, $2, 'pending')
            RETURNING id
            """,
            holder_id, season,
        )

    return {
        "holder_id": holder_id,
        "ticket_id": ticket_id,
        "status": "pending",
        "already_exists": False,
    }


async def approve_ticket(ticket_id: int, reviewed_by: str, seat_info: str = "", price: float = None) -> dict | None:
    """Approve a season ticket: generate ticket code and set password for holder."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        ticket = await conn.fetchrow(
            """
            SELECT st.id, st.holder_id, st.season, sth.vorname, sth.nachname, sth.email, sth.password_hash
            FROM season_tickets st
            JOIN season_ticket_holders sth ON sth.id = st.holder_id
            WHERE st.id = $1 AND st.status = 'pending'
            """,
            ticket_id,
        )
        if not ticket:
            return None

        ticket_code = await generate_ticket_code(ticket["season"])

        # Generate temp password only if holder has no password yet
        temp_password = None
        if not ticket["password_hash"]:
            temp_password = generate_token()[:10]
            hashed = hash_password(temp_password)
            await conn.execute(
                "UPDATE season_ticket_holders SET password_hash=$1, is_active=TRUE, updated_at=NOW() WHERE id=$2",
                hashed, ticket["holder_id"],
            )

        await conn.execute(
            """
            UPDATE season_tickets
            SET status='approved', ticket_code=$1, reviewed_by=$2,
                seat_info=$3, price=$4, approved_at=NOW(), updated_at=NOW()
            WHERE id=$5
            """,
            ticket_code, reviewed_by, seat_info or "", price, ticket_id,
        )

    return {
        "ticket_id": ticket_id,
        "holder_id": ticket["holder_id"],
        "vorname": ticket["vorname"],
        "nachname": ticket["nachname"],
        "email": ticket["email"],
        "ticket_code": ticket_code,
        "season": ticket["season"],
        "temp_password": temp_password,
    }


async def reject_ticket(ticket_id: int, reviewed_by: str, admin_notes: str = "") -> bool:
    """Reject a season ticket application."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute(
            """
            UPDATE season_tickets
            SET status='rejected', reviewed_by=$1, admin_notes=$2, updated_at=NOW()
            WHERE id=$3 AND status='pending'
            """,
            reviewed_by, admin_notes, ticket_id,
        )
        return "UPDATE 1" in result


async def get_holder_by_email(email: str) -> dict | None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM season_ticket_holders WHERE email = $1", email)
        return dict(row) if row else None


async def get_holder_by_id(holder_id: int) -> dict | None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM season_ticket_holders WHERE id = $1", holder_id)
        return dict(row) if row else None


async def get_holder_tickets(holder_id: int) -> list[dict]:
    """Get all tickets for a holder."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id, season, ticket_code, status, seat_info, price, approved_at, created_at
            FROM season_tickets
            WHERE holder_id = $1
            ORDER BY created_at DESC
            """,
            holder_id,
        )
        result = []
        for r in rows:
            d = dict(r)
            for key in ("approved_at", "created_at"):
                if d.get(key):
                    d[key] = str(d[key])
            if d.get("price"):
                d["price"] = float(d["price"])
            result.append(d)
        return result


async def get_pending_tickets() -> list[dict]:
    """Get all pending ticket applications for admin review."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT st.id, st.season, st.status, st.created_at,
                   sth.vorname, sth.nachname, sth.email, sth.telefon
            FROM season_tickets st
            JOIN season_ticket_holders sth ON sth.id = st.holder_id
            WHERE st.status = 'pending'
            ORDER BY st.created_at ASC
            """,
        )
        result = []
        for r in rows:
            d = dict(r)
            if d.get("created_at"):
                d["created_at"] = str(d["created_at"])
            result.append(d)
        return result


async def get_all_tickets(season: str = "", status: str = "") -> list[dict]:
    """Get all tickets with optional filters."""
    pool = await get_pool()
    conditions = []
    params = []
    idx = 1

    if season:
        conditions.append(f"st.season = ${idx}")
        params.append(season)
        idx += 1
    if status:
        conditions.append(f"st.status = ${idx}")
        params.append(status)
        idx += 1

    where = " AND ".join(conditions) if conditions else "TRUE"

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            f"""
            SELECT st.*, sth.vorname, sth.nachname, sth.email
            FROM season_tickets st
            JOIN season_ticket_holders sth ON sth.id = st.holder_id
            WHERE {where}
            ORDER BY st.created_at DESC
            """,
            *params,
        )
        result = []
        for r in rows:
            d = dict(r)
            for key in ("approved_at", "created_at", "updated_at"):
                if d.get(key):
                    d[key] = str(d[key])
            if d.get("price"):
                d["price"] = float(d["price"])
            result.append(d)
        return result
