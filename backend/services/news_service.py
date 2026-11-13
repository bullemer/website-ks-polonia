"""
KS Polonia – News Articles Service.
CRUD for portal-managed news articles.
"""
import re
import json
from typing import Optional, Dict, Any, List
from database import get_pool


def _slugify(text: str) -> str:
    """Generate a URL-safe slug from title."""
    text = text.lower().strip()
    # Replace German characters
    replacements = {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"}
    for k, v in replacements.items():
        text = text.replace(k, v)
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text).strip('-')
    return text[:200]


async def get_news_list(
    published_only: bool = False,
    team_id: Optional[int] = None,
    author_id: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
) -> Dict[str, Any]:
    """Get news articles with optional filters and pagination."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        conditions = []
        params = []
        idx = 1

        if published_only:
            conditions.append(f"n.is_published = TRUE")
        if team_id is not None:
            conditions.append(f"n.team_id = ${idx}")
            params.append(team_id)
            idx += 1
        if author_id is not None:
            conditions.append(f"n.author_id = ${idx}")
            params.append(author_id)
            idx += 1

        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        # Count total
        count_row = await conn.fetchrow(
            f"SELECT COUNT(*) as total FROM news_articles n {where}",
            *params
        )
        total = count_row["total"]

        # Fetch articles
        rows = await conn.fetch(f"""
            SELECT n.*, m.vorname, m.nachname, t.mannschaftsname as team_name
            FROM news_articles n
            LEFT JOIN members m ON m.id = n.author_id
            LEFT JOIN teams t ON t.id = n.team_id
            {where}
            ORDER BY COALESCE(n.published_at, n.created_at) DESC
            LIMIT ${idx} OFFSET ${idx + 1}
        """, *params, limit, offset)

        return {
            "articles": [dict(r) for r in rows],
            "total": total,
            "limit": limit,
            "offset": offset,
        }


async def get_news_article(article_id: int) -> Optional[Dict[str, Any]]:
    """Get a single news article by ID."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT n.*, m.vorname, m.nachname, t.mannschaftsname as team_name
            FROM news_articles n
            LEFT JOIN members m ON m.id = n.author_id
            LEFT JOIN teams t ON t.id = n.team_id
            WHERE n.id = $1
        """, article_id)
        return dict(row) if row else None


async def get_news_by_slug(slug: str) -> Optional[Dict[str, Any]]:
    """Get a single news article by slug."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT n.*, m.vorname, m.nachname, t.mannschaftsname as team_name
            FROM news_articles n
            LEFT JOIN members m ON m.id = n.author_id
            LEFT JOIN teams t ON t.id = n.team_id
            WHERE n.slug = $1
        """, slug)
        return dict(row) if row else None


async def create_news_article(
    title: str,
    content: str,
    author_id: int,
    summary: str = "",
    category: str = "Allgemein",
    cover_image: Optional[str] = None,
    team_id: Optional[int] = None,
    is_published: bool = False,
) -> Dict[str, Any]:
    """Create a new news article."""
    slug = _slugify(title)
    pool = await get_pool()
    async with pool.acquire() as conn:
        # Ensure unique slug
        existing = await conn.fetchval(
            "SELECT COUNT(*) FROM news_articles WHERE slug = $1", slug
        )
        if existing > 0:
            slug = f"{slug}-{existing + 1}"

        published_at = "NOW()" if is_published else None
        row = await conn.fetchrow("""
            INSERT INTO news_articles (title, slug, summary, content, category, cover_image, team_id, author_id, is_published, published_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, CASE WHEN $9 THEN NOW() ELSE NULL END)
            RETURNING *
        """, title, slug, summary, content, category, cover_image, team_id, author_id, is_published)
        return dict(row)


async def update_news_article(article_id: int, updates: Dict[str, Any]) -> bool:
    """Update an existing news article."""
    allowed = {"title", "summary", "content", "category", "cover_image", "team_id", "is_published"}
    fields = {k: v for k, v in updates.items() if k in allowed}
    if not fields:
        return True

    # If title changed, update slug too
    if "title" in fields:
        fields["slug"] = _slugify(fields["title"])

    # Handle publish/unpublish
    if "is_published" in fields and fields["is_published"]:
        fields["published_at_raw"] = True  # flag to set NOW()

    set_parts = []
    values = []
    idx = 2
    for k, v in fields.items():
        if k == "published_at_raw":
            set_parts.append("published_at = NOW()")
            continue
        set_parts.append(f"{k} = ${idx}")
        values.append(v)
        idx += 1
    set_parts.append("updated_at = NOW()")

    pool = await get_pool()
    async with pool.acquire() as conn:
        res = await conn.execute(
            f"UPDATE news_articles SET {', '.join(set_parts)} WHERE id = $1",
            article_id, *values
        )
        return "UPDATE 1" in res


async def delete_news_article(article_id: int) -> bool:
    """Delete a news article."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        res = await conn.execute("DELETE FROM news_articles WHERE id = $1", article_id)
        return "DELETE 1" in res
