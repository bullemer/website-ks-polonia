"""
KS Polonia – Database migration runner.
Executes SQL migration files using asyncpg (no psql CLI needed).
Safe for Hetzner shared hosting where psql may not be available.

Usage:
    python3 migrate.py                          # Run all pending migrations
    python3 migrate.py migrations/001_xxx.sql   # Run a specific file
"""
import asyncio
import sys
import os
import glob

# Add parent dir to path for config import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import DATABASE_URL


async def run_migration(sql_file: str):
    """Execute a single SQL migration file."""
    import asyncpg

    print(f"📄 Running: {os.path.basename(sql_file)}")

    with open(sql_file, "r") as f:
        sql = f.read()

    try:
        conn = await asyncpg.connect(DATABASE_URL)

        # Execute the entire migration as a single transaction
        await conn.execute(sql)

        # Verify: list all tables
        rows = await conn.fetch(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' ORDER BY table_name"
        )
        print(f"✅ Migration complete. Tables in database:")
        for r in rows:
            print(f"   • {r['table_name']}")

        await conn.close()
        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False


async def main():
    if len(sys.argv) > 1:
        # Run specific file
        sql_file = sys.argv[1]
        if not os.path.exists(sql_file):
            print(f"File not found: {sql_file}")
            sys.exit(1)
        success = await run_migration(sql_file)
    else:
        # Run all migrations in order
        migration_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "migrations")
        files = sorted(glob.glob(os.path.join(migration_dir, "*.sql")))
        if not files:
            print("No migration files found.")
            sys.exit(0)

        success = True
        for f in files:
            ok = await run_migration(f)
            if not ok:
                success = False
                break

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
