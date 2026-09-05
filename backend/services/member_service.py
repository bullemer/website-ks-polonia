"""
KS Polonia – Member business logic.
All database operations for members, applications, and member numbers.
"""
import datetime
from database import get_pool
from auth import hash_password, generate_token


async def generate_member_number() -> str:
    """Generate next member number in format POL-YYYY-NNNN."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        seq = await conn.fetchval("SELECT nextval('member_number_seq')")
        year = datetime.datetime.now().year
        return f"POL-{year}-{seq:04d}"


async def create_member_from_application(
    vorname: str,
    nachname: str,
    email: str,
    telefon: str,
    strasse: str,
    plz: str,
    ort: str,
    land: str,
    geburtsdatum: str,
    geschlecht: str,
    eintrittsdatum: str,
    abteilungen: str,
    trainer_referenz: str = "",
    bemerkungen: str = "",
    id_front_path: str = "",
    id_back_path: str = "",
) -> dict:
    """
    Create a new member record + membership application from the online form.
    Returns the new member dict with application_id.
    """
    pool = await get_pool()
    mitgliedsnummer = await generate_member_number()

    # Parse dates safely
    geb_date = _parse_date(geburtsdatum)
    ein_date = _parse_date(eintrittsdatum)

    async with pool.acquire() as conn:
        async with conn.transaction():
            # Determine membership_level based on selected divisions
            level = "regular"
            if abteilungen:
                div_lower = abteilungen.lower()
                if "passiv" in div_lower:
                    has_active = any(s in div_lower for s in ["fußball", "fussball", "basketball", "badminton", "volleyball"])
                    if not has_active:
                        level = "passive"

            # Insert member
            member_id = await conn.fetchval(
                """
                INSERT INTO members (
                    mitgliedsnummer, vorname, nachname, email, telefon,
                    strasse, plz, ort, land, geburtsdatum, geschlecht,
                    eintrittsdatum, id_front_path, id_back_path,
                    trainer_referenz, bemerkungen, is_active, membership_level
                ) VALUES (
                    $1, $2, $3, $4, $5,
                    $6, $7, $8, $9, $10, $11,
                    $12, $13, $14,
                    $15, $16, FALSE, $17
                )
                RETURNING id
                """,
                mitgliedsnummer, vorname, nachname, email, telefon or "",
                strasse, plz, ort, land, geb_date, geschlecht,
                ein_date, id_front_path, id_back_path,
                trainer_referenz or "", bemerkungen or "", level,
            )

            # Create application record
            app_id = await conn.fetchval(
                """
                INSERT INTO membership_applications (member_id, status)
                VALUES ($1, 'pending')
                RETURNING id
                """,
                member_id,
            )

            # Link member to selected divisions
            if abteilungen:
                division_names = [d.strip() for d in abteilungen.split(",") if d.strip()]
                for dname in division_names:
                    # Map form values to division names
                    mapped = _map_division_name(dname)
                    div_id = await conn.fetchval(
                        "SELECT id FROM divisions WHERE name = $1", mapped
                    )
                    if div_id:
                        await conn.execute(
                            """
                            INSERT INTO member_divisions (member_id, division_id, status)
                            VALUES ($1, $2, 'active')
                            ON CONFLICT (member_id, division_id) DO NOTHING
                            """,
                            member_id, div_id,
                        )

    return {
        "member_id": member_id,
        "mitgliedsnummer": mitgliedsnummer,
        "application_id": app_id,
    }


async def approve_application(app_id: int, reviewed_by: str, admin_notes: str = "") -> dict:
    """
    Approve a membership application:
    - Set application status to 'approved'
    - Activate the member account
    - Generate a temporary password
    - Return member info for the welcome email
    """
    pool = await get_pool()
    temp_password = generate_token()[:12]  # 12-char random password
    hashed = hash_password(temp_password)

    async with pool.acquire() as conn:
        async with conn.transaction():
            # Get application + member
            row = await conn.fetchrow(
                """
                SELECT ma.id, ma.member_id, m.vorname, m.nachname, m.email
                FROM membership_applications ma
                JOIN members m ON m.id = ma.member_id
                WHERE ma.id = $1 AND ma.status = 'pending'
                """,
                app_id,
            )
            if not row:
                return None

            # Update application
            await conn.execute(
                """
                UPDATE membership_applications
                SET status = 'approved', reviewed_by = $1, admin_notes = $2, reviewed_at = NOW()
                WHERE id = $3
                """,
                reviewed_by, admin_notes, app_id,
            )

            # Activate member and set password
            await conn.execute(
                """
                UPDATE members
                SET is_active = TRUE, password_hash = $1, updated_at = NOW()
                WHERE id = $2
                """,
                hashed, row["member_id"],
            )

    return {
        "member_id": row["member_id"],
        "vorname": row["vorname"],
        "nachname": row["nachname"],
        "email": row["email"],
        "temp_password": temp_password,
    }


async def reject_application(app_id: int, reviewed_by: str, admin_notes: str = "") -> bool:
    """Reject a membership application."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute(
            """
            UPDATE membership_applications
            SET status = 'rejected', reviewed_by = $1, admin_notes = $2, reviewed_at = NOW()
            WHERE id = $3 AND status = 'pending'
            """,
            reviewed_by, admin_notes, app_id,
        )
        return "UPDATE 1" in result


async def get_member_by_email(email: str) -> dict | None:
    """Fetch a member by email."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM members WHERE email = $1", email)
        return dict(row) if row else None


async def get_member_by_id(member_id: int) -> dict | None:
    """Fetch a member by ID."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM members WHERE id = $1", member_id)
        return dict(row) if row else None


async def update_member_profile(member_id: int, updates: dict) -> bool:
    """Update member profile fields. Only non-None values are updated."""
    fields = {k: v for k, v in updates.items() if v is not None}
    if not fields:
        return False

    if "role" in fields:
        fields["is_admin"] = fields["role"] in ("superadmin", "admin")

    # Safely convert date strings to date objects for PostgreSQL
    for df in ("geburtsdatum", "eintrittsdatum"):
        if df in fields:
            if isinstance(fields[df], str):
                fields[df] = _parse_date(fields[df]) if fields[df].strip() else None
            elif not isinstance(fields[df], (datetime.date, datetime.datetime)):
                fields[df] = None

    set_clauses = ", ".join(f"{k} = ${i+2}" for i, k in enumerate(fields.keys()))
    values = [member_id] + list(fields.values())

    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute(
            f"UPDATE members SET {set_clauses}, updated_at = NOW() WHERE id = $1",
            *values,
        )
        return "UPDATE 1" in result


async def update_bank_account(member_id: int, kontoinhaber: str, iban: str, bic: str = "", bank_name: str = "") -> int:
    """Insert or update the active bank account for a member."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        # Deactivate previous accounts
        await conn.execute(
            "UPDATE member_bank_accounts SET is_active = FALSE WHERE member_id = $1",
            member_id,
        )
        # Insert new active account
        new_id = await conn.fetchval(
            """
            INSERT INTO member_bank_accounts (member_id, kontoinhaber, iban, bic, bank_name, is_active)
            VALUES ($1, $2, $3, $4, $5, TRUE)
            RETURNING id
            """,
            member_id, kontoinhaber, iban, bic or "", bank_name or "",
        )
        return new_id


async def get_bank_account(member_id: int) -> dict | None:
    """Get the active bank account for a member."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM member_bank_accounts WHERE member_id = $1 AND is_active = TRUE",
            member_id,
        )
        return dict(row) if row else None


async def get_member_divisions(member_id: int) -> list[dict]:
    """Get all division memberships for a member."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT md.id, md.status, md.joined_at, d.name, d.sport, d.icon
            FROM member_divisions md
            JOIN divisions d ON d.id = md.division_id
            WHERE md.member_id = $1
            ORDER BY d.sort_order
            """,
            member_id,
        )
        return [dict(r) for r in rows]


async def get_member_teams(member_id: int) -> list[dict]:
    """Get all team assignments for a member."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT mt.id, mt.position, mt.jersey_number, mt.status, mt.joined_at,
                   t.mannschaftsname, t.mannschaftsart, t.spielklasse,
                   d.name as division_name
            FROM member_teams mt
            JOIN teams t ON t.id = mt.team_id
            LEFT JOIN divisions d ON d.id = t.division_id
            WHERE mt.member_id = $1
            ORDER BY d.sort_order, t.sort_order
            """,
            member_id,
        )
        return [dict(r) for r in rows]


async def list_members(
    search: str = "",
    division_id: int | None = None,
    is_active: bool | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[dict], int]:
    """
    List members with optional search, division filter, and pagination.
    Returns (members, total_count).
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        conditions = []
        params = []
        param_idx = 1

        if search:
            conditions.append(
                f"(m.vorname ILIKE ${param_idx} OR m.nachname ILIKE ${param_idx} "
                f"OR m.email ILIKE ${param_idx} OR m.mitgliedsnummer ILIKE ${param_idx})"
            )
            params.append(f"%{search}%")
            param_idx += 1

        if division_id is not None:
            conditions.append(
                f"EXISTS (SELECT 1 FROM member_divisions md WHERE md.member_id = m.id AND md.division_id = ${param_idx})"
            )
            params.append(division_id)
            param_idx += 1

        if is_active is not None:
            conditions.append(f"m.is_active = ${param_idx}")
            params.append(is_active)
            param_idx += 1

        where = " AND ".join(conditions) if conditions else "TRUE"

        # Count
        total = await conn.fetchval(
            f"SELECT COUNT(*) FROM members m WHERE {where}", *params
        )

        # Fetch page
        rows = await conn.fetch(
            f"""
            SELECT m.id, m.mitgliedsnummer, m.vorname, m.nachname, m.email,
                   m.membership_level, m.role, m.is_active, m.is_admin, m.eintrittsdatum,
                   STRING_AGG(d.name, ', ' ORDER BY d.sort_order) as divisions
            FROM members m
            LEFT JOIN member_divisions md ON md.member_id = m.id AND md.status = 'active'
            LEFT JOIN divisions d ON d.id = md.division_id
            WHERE {where}
            GROUP BY m.id
            ORDER BY m.nachname, m.vorname
            LIMIT ${param_idx} OFFSET ${param_idx + 1}
            """,
            *params, limit, offset,
        )

        return [dict(r) for r in rows], total


async def get_pending_applications() -> list[dict]:
    """Get all pending membership applications with member info."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT ma.id, ma.member_id, ma.status, ma.submitted_at,
                   m.vorname, m.nachname, m.email, m.geburtsdatum,
                   STRING_AGG(d.name, ', ') as abteilungen
            FROM membership_applications ma
            JOIN members m ON m.id = ma.member_id
            LEFT JOIN member_divisions md ON md.member_id = m.id
            LEFT JOIN divisions d ON d.id = md.division_id
            WHERE ma.status = 'pending'
            GROUP BY ma.id, m.id
            ORDER BY ma.submitted_at ASC
            """,
        )
        return [dict(r) for r in rows]


async def get_dashboard_stats() -> dict:
    """Get stats for the admin dashboard."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        total = await conn.fetchval("SELECT COUNT(*) FROM members")
        active = await conn.fetchval("SELECT COUNT(*) FROM members WHERE is_active = TRUE")
        pending = await conn.fetchval(
            "SELECT COUNT(*) FROM membership_applications WHERE status = 'pending'"
        )

        div_stats = await conn.fetch(
            """
            SELECT d.name, d.icon, COUNT(md.member_id) as count
            FROM divisions d
            LEFT JOIN member_divisions md ON md.division_id = d.id AND md.status = 'active'
            WHERE d.is_active = TRUE
            GROUP BY d.id
            ORDER BY d.sort_order
            """
        )

        return {
            "total_members": total,
            "active_members": active,
            "pending_applications": pending,
            "divisions": [dict(r) for r in div_stats],
        }


# ═══════════════════════════════════════
#  PAYMENT TRACKING
# ═══════════════════════════════════════

async def get_member_payments(member_id: int, limit: int = 50) -> list[dict]:
    """Get payment history for a member, newest first."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id, amount, description, period, payment_date,
                   payment_method, status, notes, created_at
            FROM member_payments
            WHERE member_id = $1
            ORDER BY payment_date DESC, created_at DESC
            LIMIT $2
            """,
            member_id, limit,
        )
        result = []
        for r in rows:
            d = dict(r)
            for key in ("payment_date", "created_at"):
                if d.get(key):
                    d[key] = str(d[key])
            d["amount"] = float(d["amount"])
            result.append(d)
        return result


async def get_payment_summary(member_id: int) -> dict:
    """Get payment summary for a member."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT COUNT(*) as total_payments,
                   COALESCE(SUM(amount), 0) as total_paid,
                   MAX(payment_date) as last_payment_date
            FROM member_payments
            WHERE member_id = $1 AND status = 'received'
            """,
            member_id,
        )
        return {
            "total_payments": row["total_payments"],
            "total_paid": float(row["total_paid"]),
            "last_payment_date": str(row["last_payment_date"]) if row["last_payment_date"] else None,
        }


async def create_payment(
    member_id: int,
    amount: float,
    description: str,
    period: str = "",
    payment_date: str = "",
    payment_method: str = "Überweisung",
    status: str = "received",
    notes: str = "",
    created_by: str = "",
) -> int:
    """Create a new payment record (admin function)."""
    pool = await get_pool()
    pay_date = _parse_date(payment_date) if payment_date else datetime.date.today()
    async with pool.acquire() as conn:
        new_id = await conn.fetchval(
            """
            INSERT INTO member_payments (
                member_id, amount, description, period, payment_date,
                payment_method, status, notes, created_by
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING id
            """,
            member_id, amount, description, period or "",
            pay_date, payment_method, status, notes or "", created_by,
        )
        return new_id


async def delete_payment(payment_id: int) -> bool:
    """Delete a payment record (admin function)."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute(
            "DELETE FROM member_payments WHERE id = $1", payment_id
        )
        return "DELETE 1" in result


# --- Helpers ---

def _parse_date(date_str: str):
    """Parse date string to date object, returns None on failure."""
    if not date_str:
        return None
    try:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        try:
            return datetime.datetime.strptime(date_str, "%d.%m.%Y").date()
        except ValueError:
            return None


def _map_division_name(form_value: str) -> str:
    """Map form checkbox values to division names in the DB."""
    mapping = {
        "Badminton": "Badminton",
        "Basketball (Seniors)": "Basketball",
        "Basketball (Juniors)": "Basketball",
        "Fußball Herren": "Fußball",
        "Fußball Jugend": "Fußball",
        "Volleyball": "Volleyball",
        "Passive Mitglieder": "Passive Mitglieder",
        "Passives Mitglied": "Passive Mitglieder",
        "Passive Mitgliedschaft": "Passive Mitglieder",
        "Passiv": "Passive Mitglieder",
    }
    return mapping.get(form_value, form_value)

