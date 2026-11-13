-- Migration 026: News articles table for portal-managed news
-- Allows team officials to write news/blog posts that appear on the website

CREATE TABLE IF NOT EXISTS news_articles (
    id            SERIAL PRIMARY KEY,
    title         VARCHAR(500) NOT NULL,
    slug          VARCHAR(500) NOT NULL UNIQUE,
    summary       TEXT DEFAULT '',
    content       TEXT NOT NULL DEFAULT '',
    category      VARCHAR(50) NOT NULL DEFAULT 'Allgemein',
    cover_image   TEXT,         -- URL to uploaded cover image
    team_id       INT REFERENCES teams(id) ON DELETE SET NULL,
    author_id     INT NOT NULL REFERENCES members(id) ON DELETE CASCADE,
    is_published  BOOLEAN NOT NULL DEFAULT FALSE,
    published_at  TIMESTAMPTZ,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_news_articles_published ON news_articles(is_published, published_at DESC);
CREATE INDEX IF NOT EXISTS idx_news_articles_team ON news_articles(team_id);
CREATE INDEX IF NOT EXISTS idx_news_articles_slug ON news_articles(slug);
