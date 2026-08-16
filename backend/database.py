"""
KS Polonia – Database connection pool (asyncpg).
Replaces per-request connect() calls with a shared pool for performance.
"""
import asyncpg
from config import DATABASE_URL

_pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    """Return the shared connection pool, creating it on first call."""
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=2,
            max_size=10,
            command_timeout=30,
        )
    return _pool


async def close_pool():
    """Gracefully close the pool (call on app shutdown)."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
