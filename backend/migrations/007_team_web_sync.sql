-- Migration 007: Team web sync, trainingszeiten, and basketball teams
ALTER TABLE teams ADD COLUMN IF NOT EXISTS training_times TEXT;
ALTER TABLE teams ADD COLUMN IF NOT EXISTS training_location TEXT;
ALTER TABLE teams ADD COLUMN IF NOT EXISTS contact_person TEXT;
ALTER TABLE teams ADD COLUMN IF NOT EXISTS webpage_url TEXT;
ALTER TABLE teams ADD COLUMN IF NOT EXISTS content TEXT;
ALTER TABLE teams ADD COLUMN IF NOT EXISTS gallery JSONB DEFAULT '[]'::jsonb;

-- Ensure Basketball Teams exist
INSERT INTO teams (
    nummer, vereinsname, mannschaftsart, mannschaftsname, spielklasse, 
    status, division_id, coach, is_active, sort_order, 
    training_times, training_location, contact_person, webpage_url
) 
SELECT 
    'BB-U10', 'Polonia', 'Jugend U10', 'Basketball U10 (Jugend)', 'Kinderbasketball',
    'aktiv', 2, 'Carsten Bullemer', TRUE, 1,
    'Dienstag, 17:00 – 18:30 Uhr', 'Schulsporthalle Uferstraße 10, 22081 Hamburg',
    'Carsten Bullemer', '/seiten/basketball-jugend-u10'
WHERE NOT EXISTS (
    SELECT 1 FROM teams WHERE mannschaftsname ILIKE '%Basketball%U10%'
);

INSERT INTO teams (
    nummer, vereinsname, mannschaftsart, mannschaftsname, spielklasse, 
    status, division_id, coach, is_active, sort_order, 
    training_times, training_location, contact_person, webpage_url
) 
SELECT 
    'BB-UE35', 'Polonia', 'Herren Ü35', 'Basketball Herren Ü35', 'Freizeitliga',
    'aktiv', 2, 'Carsten Bullemer', TRUE, 2,
    'Dienstag, 18:30 – 20:00 Uhr', 'Schulsporthalle Uferstraße 10, 22081 Hamburg',
    'Carsten Bullemer', '/seiten/basketball-herren-ue35'
WHERE NOT EXISTS (
    SELECT 1 FROM teams WHERE mannschaftsname ILIKE '%Basketball%Ü35%' OR mannschaftsname ILIKE '%Basketball%Ue35%'
);

-- Update E-Junioren web url
UPDATE teams
SET webpage_url = '/football/e-junioren'
WHERE id = 11 AND (webpage_url IS NULL OR webpage_url = '');

-- Assign Carsten Bullemer (member 3) as manager to the 3 teams
INSERT INTO member_teams (member_id, team_id, role, position, status)
SELECT 3, t.id, 'manager', 'Mannschaftsverantwortlicher', 'active'
FROM teams t
WHERE t.id = 11 OR t.mannschaftsname ILIKE '%Basketball%U10%' OR t.mannschaftsname ILIKE '%Basketball%Ü35%'
ON CONFLICT (member_id, team_id) DO UPDATE
SET role = 'manager', position = 'Mannschaftsverantwortlicher', status = 'active';
