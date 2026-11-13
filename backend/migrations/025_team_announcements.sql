-- Migration 025: Team announcements table + external_url + webpage_url population
-- Allows team officials to post news/announcements for their team page

CREATE TABLE IF NOT EXISTS team_announcements (
    id           SERIAL PRIMARY KEY,
    team_id      INT NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    title        VARCHAR(255) NOT NULL,
    content      TEXT NOT NULL DEFAULT '',
    is_active    BOOLEAN NOT NULL DEFAULT TRUE,
    created_by   INT REFERENCES members(id) ON DELETE SET NULL,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_team_announcements_team ON team_announcements(team_id);
CREATE INDEX IF NOT EXISTS idx_team_announcements_active ON team_announcements(team_id, is_active);

-- Add external_url column for fussball.de team link
ALTER TABLE teams ADD COLUMN IF NOT EXISTS external_url TEXT;

-- Populate webpage_url for all football teams (for slug-based announcement lookup)
UPDATE teams SET webpage_url = '/football/1-herren' WHERE mannschaftsname ILIKE '%1.Herren%' AND (webpage_url IS NULL OR webpage_url = '');
UPDATE teams SET webpage_url = '/football/2-herren' WHERE mannschaftsname ILIKE '%2.Herren%' AND (webpage_url IS NULL OR webpage_url = '');
UPDATE teams SET webpage_url = '/football/3-herren' WHERE mannschaftsname ILIKE '%3.Herren%' AND (webpage_url IS NULL OR webpage_url = '');
UPDATE teams SET webpage_url = '/football/4-herren' WHERE mannschaftsname ILIKE '%4.Herren%' AND (webpage_url IS NULL OR webpage_url = '');
UPDATE teams SET webpage_url = '/football/ue40-herren' WHERE mannschaftsname ILIKE '%Ü40%' AND (webpage_url IS NULL OR webpage_url = '');
UPDATE teams SET webpage_url = '/football/ue50-herren' WHERE mannschaftsname ILIKE '%Ü50%' AND (webpage_url IS NULL OR webpage_url = '');
UPDATE teams SET webpage_url = '/football/c-junioren-1' WHERE mannschaftsname ILIKE '%1.C-Jun%' AND (webpage_url IS NULL OR webpage_url = '');
UPDATE teams SET webpage_url = '/football/c-junioren-2' WHERE mannschaftsname ILIKE '%2.C-Jun%' AND (webpage_url IS NULL OR webpage_url = '');
UPDATE teams SET webpage_url = '/football/d-junioren' WHERE mannschaftsname ILIKE '%D-Jun%' AND (webpage_url IS NULL OR webpage_url = '');
