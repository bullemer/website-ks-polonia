-- Migration 000: Bootstrap migration tracking
-- Only seeds migrations that are NOT idempotent (would fail on re-run).
-- All others will be re-run safely to ensure they are applied.

CREATE TABLE IF NOT EXISTS _migrations (
    filename TEXT PRIMARY KEY,
    applied_at TIMESTAMPTZ DEFAULT NOW()
);

-- These 3 have ALTER TABLE ADD COLUMN without IF NOT EXISTS,
-- so they would fail if run again on an existing database.
INSERT INTO _migrations (filename) VALUES
    ('001_membership_system.sql'),
    ('004_team_roles.sql'),
    ('006_roles_and_team_management.sql')
ON CONFLICT (filename) DO NOTHING;
