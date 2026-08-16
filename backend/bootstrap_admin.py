"""
Bootstrap first admin user.
Run once: python3 bootstrap_admin.py
"""
import asyncio
import asyncpg
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from auth import hash_password
from config import DATABASE_URL


async def main():
    conn = await asyncpg.connect(DATABASE_URL)

    existing = await conn.fetchrow(
        "SELECT id FROM members WHERE email = $1", "info@ks-polonia.de"
    )
    if existing:
        print(f"Admin already exists (ID: {existing['id']})")
        await conn.close()
        return

    hashed = hash_password("Polonia2026!")
    member_id = await conn.fetchval(
        "INSERT INTO members (mitgliedsnummer, vorname, nachname, email, password_hash, "
        "is_admin, is_active, email_verified, membership_level) "
        "VALUES ($1, $2, $3, $4, $5, TRUE, TRUE, TRUE, $6) RETURNING id",
        "POL-2026-0000", "Admin", "Polonia", "info@ks-polonia.de", hashed, "admin",
    )

    print(f"Admin created! ID: {member_id}")
    print(f"Email: info@ks-polonia.de")
    print(f"Password: Polonia2026!")
    await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
