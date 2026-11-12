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

-- Remove entries for idempotent migrations that may have been
-- seeded by a previous version of this bootstrap but never actually ran.
DELETE FROM _migrations WHERE filename IN (
    '002_payments.sql',
    '003_season_tickets.sql',
    '005_passive_members_division.sql',
    '007_team_web_sync.sql',
    '008_basketball_u12.sql',
    '009_dedup_teams.sql',
    '010_player_fields.sql',
    '011_import_e_junioren.sql',
    '012_import_2c_junioren.sql'
);
