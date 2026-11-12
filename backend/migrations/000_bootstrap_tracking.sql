-- Migration 000: Bootstrap migration tracking
-- Seeds the _migrations table with all previously-applied migrations
-- so the runner skips them on future deploys.

CREATE TABLE IF NOT EXISTS _migrations (
    filename TEXT PRIMARY KEY,
    applied_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO _migrations (filename) VALUES
    ('001_membership_system.sql'),
    ('002_payments.sql'),
    ('003_season_tickets.sql'),
    ('004_team_roles.sql'),
    ('005_passive_members_division.sql'),
    ('006_roles_and_team_management.sql'),
    ('007_team_web_sync.sql'),
    ('008_basketball_u12.sql'),
    ('009_dedup_teams.sql'),
    ('010_player_fields.sql'),
    ('011_import_e_junioren.sql'),
    ('012_import_2c_junioren.sql')
ON CONFLICT (filename) DO NOTHING;
