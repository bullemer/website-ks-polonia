"""
Database migration & seed script for the Wall of Honor (donor_spots table).
Run once to create the table and insert 79 initial spots.

Usage:
    python init_wall.py
"""
import asyncio
import asyncpg

DATABASE_URL = "postgresql://trusteei_0:k6%25KkhF%3B%29FY4@kwnz.your-database.de:5432/kspolonia"

# Spot layout: (category, count)
SPOT_LAYOUT = [
    ("platin", 2),
    ("gold", 2),
    ("traeger", 5),
    ("silber", 20),
    ("kibice", 50),
]


async def main():
    conn = await asyncpg.connect(DATABASE_URL)

    # Create table
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS donor_spots (
            id SERIAL PRIMARY KEY,
            category VARCHAR(20) NOT NULL,
            position INTEGER NOT NULL,
            donor_name VARCHAR(200),
            donor_message VARCHAR(500),
            status VARCHAR(20) NOT NULL DEFAULT 'available',
            transaction_id VARCHAR(100),
            reserved_at TIMESTAMPTZ,
            confirmed_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
    """)

    # Create index
    await conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_donor_spots_category ON donor_spots(category);
    """)
    await conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_donor_spots_status ON donor_spots(status);
    """)

    # Check if already seeded
    count = await conn.fetchval("SELECT COUNT(*) FROM donor_spots")
    if count > 0:
        print(f"Table already has {count} rows — skipping seed.")
        await conn.close()
        return

    # Seed spots
    position = 1
    for category, num in SPOT_LAYOUT:
        for _ in range(num):
            await conn.execute(
                "INSERT INTO donor_spots (category, position, status) VALUES ($1, $2, 'available')",
                category, position,
            )
            position += 1

    total = await conn.fetchval("SELECT COUNT(*) FROM donor_spots")
    print(f"✅ Seeded {total} donor spots successfully.")
    await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
