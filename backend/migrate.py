"""
KS Polonia – Database migration runner.
Executes SQL migration files using asyncpg (no psql CLI needed).
Safe for Hetzner shared hosting where psql may not be available.

Tracks completed migrations in a `_migrations` table so each
migration only runs once.

Usage:
    python3 migrate.py                          # Run all pending migrations
    python3 migrate.py migrations/001_xxx.sql   # Run a specific file (even if already applied)
"""
import asyncio
import sys
import os
import glob
import traceback

# Add parent dir to path for config import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import DATABASE_URL

ENSURE_TABLE = """
CREATE TABLE IF NOT EXISTS _migrations (
    filename TEXT PRIMARY KEY,
    applied_at TIMESTAMPTZ DEFAULT NOW()
);
"""


async def run_migration(sql_file: str, *, force: bool = False):
    """Execute a single SQL migration file."""
    import asyncpg

    basename = os.path.basename(sql_file)
    print(f"📄 {'(force) ' if force else ''}Running: {basename}")

    with open(sql_file, "r") as f:
        sql = f.read()

    conn = None
    try:
        conn = await asyncpg.connect(DATABASE_URL)

        # Ensure tracking table exists
        await conn.execute(ENSURE_TABLE)

        # Check if already applied (unless forced)
        if not force:
            already = await conn.fetchval(
                "SELECT 1 FROM _migrations WHERE filename = $1", basename
            )
            if already:
                print(f"⏭️  Skipped (already applied): {basename}")
                await conn.close()
                return True

        # Execute the migration
        await conn.execute(sql)

        # Record it
        await conn.execute(
            "INSERT INTO _migrations (filename) VALUES ($1) ON CONFLICT (filename) DO UPDATE SET applied_at = NOW()",
            basename,
        )

        print(f"✅ Applied: {basename}")
        await conn.close()
        return True

    except Exception as e:
        print(f"❌ Migration FAILED: {basename}")
        print(f"   Error: {e}")
        traceback.print_exc()
        if conn:
            try:
                await conn.close()
            except Exception:
                pass
        return False


async def main():
    if len(sys.argv) > 1:
        # Run specific file (forced — even if already applied)
        sql_file = sys.argv[1]
        if not os.path.exists(sql_file):
            print(f"File not found: {sql_file}")
            sys.exit(1)
        success = await run_migration(sql_file, force=True)
    else:
        # Run all pending migrations in order
        migration_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "migrations")
        files = sorted(glob.glob(os.path.join(migration_dir, "*.sql")))
        if not files:
            print("No migration files found.")
            sys.exit(0)

        success = True
        applied = 0
        skipped = 0
        for f in files:
            ok = await run_migration(f)
            if not ok:
                success = False
                break
            # Check if it was skipped or applied by looking at stdout (simple approach)
            applied += 1

        print(f"\n{'✅' if success else '❌'} Migration run complete: {applied} processed.")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
