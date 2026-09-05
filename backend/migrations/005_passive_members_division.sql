-- Migration 005: Add 'Passive Mitglieder' division
INSERT INTO divisions (name, sport, icon, description, sort_order)
VALUES ('Passive Mitglieder', 'Passiv', '🤝', 'Passive Mitgliedschaft & Fördermitglieder', 5)
ON CONFLICT (name) DO NOTHING;
