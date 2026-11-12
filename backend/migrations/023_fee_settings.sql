-- Migration 023: Fee Settings (Beitragseinstellungen)
-- Allows per-division and per-team monthly fee configuration.
-- Lookup priority: team-specific fee > division fee > default 15.00€

CREATE TABLE IF NOT EXISTS fee_settings (
    id SERIAL PRIMARY KEY,
    division_id INT REFERENCES divisions(id) ON DELETE CASCADE,
    team_id INT REFERENCES teams(id) ON DELETE CASCADE,
    monthly_amount NUMERIC(10,2) NOT NULL DEFAULT 15.00,
    description VARCHAR(255),
    valid_from DATE DEFAULT '2024-01-01',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(division_id, team_id)
);

-- Seed default fees per division:

-- Adult football (Fußball division, no specific team) = 20.00
INSERT INTO fee_settings (division_id, monthly_amount, description)
SELECT id, 20.00, 'Fußball Erwachsene'
FROM divisions WHERE name = 'Fußball'
ON CONFLICT DO NOTHING;

-- Basketball = 15.00
INSERT INTO fee_settings (division_id, monthly_amount, description)
SELECT id, 15.00, 'Basketball'
FROM divisions WHERE name = 'Basketball'
ON CONFLICT DO NOTHING;

-- Volleyball = 15.00
INSERT INTO fee_settings (division_id, monthly_amount, description)
SELECT id, 15.00, 'Volleyball'
FROM divisions WHERE name = 'Volleyball'
ON CONFLICT DO NOTHING;

-- Youth football teams = 15.00 (override division-level 20€)
INSERT INTO fee_settings (team_id, monthly_amount, description)
SELECT id, 15.00, 'Jugendfußball'
FROM teams WHERE mannschaftsname ILIKE '%Jun%' OR mannschaftsname ILIKE '%Junioren%'
ON CONFLICT DO NOTHING;
