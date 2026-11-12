-- ============================================================
-- Migration 016: Import 3.Herren team roster
--
-- Team: Polonia 3.Hr. | Kreisklasse | Herren
-- 48 players (no separate officials listed)
-- Several players shared with 1.Herren / 2.Herren (handled via ON CONFLICT)
-- ============================================================

DO $$
DECLARE
    v_team_id    INT;
    v_div_id     INT;
    v_member_id  INT;
    v_token      VARCHAR(100);
BEGIN
    SELECT id INTO v_div_id FROM divisions WHERE name = 'Fußball' AND is_active = TRUE LIMIT 1;
    IF v_div_id IS NULL THEN RAISE EXCEPTION 'Fußball division not found'; END IF;

    -- Find or create 3.Herren
    SELECT id INTO v_team_id FROM teams
    WHERE (mannschaftsname ILIKE '%3.Hr%' OR mannschaftsname ILIKE '%3.Herren%') AND is_active = TRUE AND division_id = v_div_id LIMIT 1;

    IF v_team_id IS NULL THEN
        INSERT INTO teams (nummer, vereinsname, mannschaftsart, mannschaftsname, spielklasse, status, division_id, is_active, sort_order)
        VALUES ('3.Hr', 'KS Polonia Hamburg', 'Herren', 'Polonia 3.Herren', 'Kreisklasse', 'aktiv', v_div_id, TRUE, 3)
        RETURNING id INTO v_team_id;
        RAISE NOTICE 'Created 3.Herren team with id %', v_team_id;
    ELSE
        RAISE NOTICE 'Using existing 3.Herren team with id %', v_team_id;
    END IF;

    -- ─── 1. Ahmad, Naeem ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Naeem', 'Ahmad', '1983-04-24', 'männlich', 'D', '0102-2870', TRUE, '2024-10-23', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0102-2870'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2024-10-23', '2026-08-23')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 2. Ait Abdelmalik, Amin ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Amin', 'Ait Abdelmalik', '2006-05-06', 'männlich', 'D', '0375-7277', TRUE, '2025-09-03', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0375-7277'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-09-03', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 3. Baradonski, Milosz Krzysztof ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Milosz Krzysztof', 'Baradonski', '2005-09-09', 'männlich', 'PL', '0787-5002', TRUE, '2026-08-27', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0787-5002'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2026-08-27', '2026-08-27')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 4. Behm, Philip ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Philip', 'Behm', '2000-10-28', 'männlich', 'D', '0672-2761', TRUE, '2026-07-11', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0672-2761'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2026-07-11', '2026-07-11')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 5. Bengui, Kyakuw Christopher (shared with 1.Hr) ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Kyakuw Christopher', 'Bengui', '1996-08-10', 'männlich', 'ZW', '0805-0414', TRUE, '2026-08-06', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0805-0414'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2026-08-06', '2026-09-06')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 6. Bintz, Tobias Benjamin Pepe (shared with 1.Hr) — Teamoffizieller ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, email, strasse, plz, ort, is_active, eintrittsdatum, claim_token)
    VALUES ('Tobias Benjamin Pepe', 'Bintz', '2005-03-23', 'männlich', 'D', '0381-1871', 'Tobias.Bintz@gmx.de', 'Erika-Mann-Bogen 9', '22081', 'Hamburg', TRUE, '2025-08-14', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  email = COALESCE(EXCLUDED.email, members.email),
                  strasse = EXCLUDED.strasse, plz = EXCLUDED.plz, ort = EXCLUDED.ort,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0381-1871'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'teamoffizieller', 'active', '2025-08-14', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET role = 'teamoffizieller', spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 7. Blochberger, Finn Collin ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Finn Collin', 'Blochberger', '2004-10-16', 'männlich', 'D', '0631-7940', TRUE, '2025-06-12', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0631-7940'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-06-12', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 8. Bohnet-Waldraff, Jan Folker ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Jan Folker', 'Bohnet-Waldraff', '2004-06-02', 'männlich', 'D', '0763-6503', TRUE, '2025-06-28', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0763-6503'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-06-28', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 9. Bruhn, Theodor Philipp Titus ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Theodor Philipp Titus', 'Bruhn', '2005-02-05', 'männlich', 'D', '0316-3969', TRUE, '2025-05-21', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0316-3969'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-05-21', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 10. Buchii, Taras (shared with 2.Hr) ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Taras', 'Buchii', '1994-06-05', 'männlich', 'UA', '0763-6390', TRUE, '2025-06-29', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0763-6390'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-06-29', '2026-08-23')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 11. Daoud, Miguel Aziz ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Miguel Aziz', 'Daoud', '2005-09-02', 'männlich', 'D', '0631-0081', TRUE, '2025-05-21', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0631-0081'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-05-21', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 12. Dilcher, Per Matti ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Per Matti', 'Dilcher', '2007-05-18', 'männlich', 'D', '0354-2139', TRUE, '2026-01-06', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0354-2139'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2026-01-06', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 13. Draeger, Philipp Jerome ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Philipp Jerome', 'Draeger', '2001-08-15', 'männlich', 'D', '0092-6928', TRUE, '2025-10-26', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0092-6928'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-10-26', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 14. Gottschalk, Jannik (Zweitspielrecht) ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Jannik', 'Gottschalk', '2003-01-16', 'männlich', 'D', '0222-1469', TRUE, '2026-07-24', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0222-1469'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2026-07-24', '2026-07-22')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 15. Groß, Jonah Nthando (shared with 1.Hr) ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Jonah Nthando', 'Groß', '2004-05-31', 'männlich', 'D', '0813-4721', TRUE, '2026-09-16', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0813-4721'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2026-09-16', '2026-09-19')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 16. Heine, Theo Bill (no Spielrecht dates) ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Theo Bill', 'Heine', '2005-02-14', 'männlich', 'D', '0338-4192', TRUE, CURRENT_DATE, v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0338-4192'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 17. Helms, Leonard ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Leonard', 'Helms', '2005-06-13', 'männlich', 'D', '0809-6177', TRUE, '2026-08-31', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0809-6177'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2026-08-31', '2026-09-04')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 18. Hill, Jacques ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Jacques', 'Hill', '1998-11-06', 'männlich', 'D', '0812-2816', TRUE, '2026-09-11', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0812-2816'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2026-09-11', '2026-09-15')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 19. Höfle, Jakob ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Jakob', 'Höfle', '2005-01-17', 'männlich', 'D', '0631-7937', TRUE, '2025-06-05', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0631-7937'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-06-05', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 20. Höfle, Theo ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Theo', 'Höfle', '2009-05-07', 'männlich', 'D', '0671-8218', TRUE, '2026-01-03', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0671-8218'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2026-01-03', '2026-07-17')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 21. Horni, Niklas Frederic ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Niklas Frederic', 'Horni', '2004-09-01', 'männlich', 'D', '0767-5349', TRUE, '2025-07-27', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0767-5349'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-07-27', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 22. Hüttmeyer, Julius ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Julius', 'Hüttmeyer', '2004-09-14', 'männlich', 'D', '0760-1315', TRUE, '2025-05-22', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0760-1315'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-05-22', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 23. Kaminski, Damian ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Damian', 'Kaminski', '2005-12-02', 'männlich', 'D', '0458-2168', TRUE, '2026-08-27', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0458-2168'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2026-08-27', '2026-07-13')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 24. Karkhane, Saeid (shared with 1.Hr) ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Saeid', 'Karkhane', '1990-01-01', 'männlich', 'IR', '0481-1163', TRUE, '2026-08-04', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0481-1163'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2026-08-04', '2026-08-23')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 25. Köhler, Gregor ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Gregor', 'Köhler', '2004-10-17', 'männlich', 'D', '0354-7570', TRUE, '2025-05-21', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0354-7570'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-05-21', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 26. Kolle, Arthur Kurt Bruno ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Arthur Kurt Bruno', 'Kolle', '2002-01-30', 'männlich', 'D', '0283-7742', TRUE, '2025-09-12', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0283-7742'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-09-12', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 27. Kuhlmann, Julian ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Julian', 'Kuhlmann', '2003-02-01', 'männlich', 'D', '0774-9189', TRUE, '2025-09-11', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0774-9189'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-09-11', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 28. Luna-Schriever, Valentin Santos ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Valentin Santos', 'Luna-Schriever', '2005-05-24', 'männlich', 'D', '0406-5901', TRUE, '2025-06-05', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0406-5901'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-06-05', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 29. Marchewski, Paul (Zweitspielrecht) ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Paul', 'Marchewski', '2002-07-15', 'männlich', 'D', '0237-0691', TRUE, '2026-07-21', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0237-0691'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2026-07-21', '2026-07-22')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 30. Mcginn, Laurence James Edward ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Laurence James Edward', 'Mcginn', '2003-08-24', 'männlich', 'GB', '0782-1780', TRUE, '2025-10-27', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0782-1780'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-10-27', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 31. Meki, Frank Ugbomor ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Frank Ugbomor', 'Meki', '2003-04-30', 'männlich', 'D', '0329-9339', TRUE, '2027-01-01', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0329-9339'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2027-01-01', '2026-09-10')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 32. Michaels, Felix ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Felix', 'Michaels', '2007-12-07', 'männlich', 'D', '0430-4709', TRUE, '2026-07-01', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0430-4709'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2026-07-01', '2026-07-09')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 33. Miranda Zerr, Philipp Leonard ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Philipp Leonard', 'Miranda Zerr', '2005-09-16', 'männlich', 'D', '0424-3918', TRUE, '2025-06-12', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0424-3918'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-06-12', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 34. Mohilat, Vlas (shared with 1.Hr) ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Vlas', 'Mohilat', '2003-08-12', 'männlich', 'UA', '0814-3815', TRUE, '2026-09-18', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0814-3815'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2026-09-18', '2026-10-25')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 35. Nolting, Moritz ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Moritz', 'Nolting', '2004-04-14', 'männlich', 'D', '0789-2872', TRUE, '2026-02-24', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0789-2872'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2026-02-24', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 36. Omar, Maxim (shared with 1.Hr) ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Maxim', 'Omar', '2003-06-20', 'männlich', 'D', '0720-0110', TRUE, '2026-07-29', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0720-0110'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2026-07-29', '2026-08-23')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 37. Owusu, Tony (shared with 1.Hr) ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Tony', 'Owusu', '2007-04-07', 'männlich', 'D', '0517-2423', TRUE, '2025-08-21', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0517-2423'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-08-21', '2026-08-23')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 38. Ravens, Niklas Maksim ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Niklas Maksim', 'Ravens', '2005-06-05', 'männlich', 'D', '0669-9913', TRUE, '2025-09-25', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0669-9913'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-09-25', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 39. Schierhorn, Liam River Janson ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Liam River Janson', 'Schierhorn', '2005-02-16', 'männlich', 'D', '0300-0232', TRUE, '2025-05-21', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0300-0232'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-05-21', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 40. Schuler, Lasse Mats ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Lasse Mats', 'Schuler', '2004-09-19', 'männlich', 'D', '0459-3503', TRUE, '2025-06-27', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0459-3503'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-06-27', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 41. Steffen, Ruben Levi ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Ruben Levi', 'Steffen', '2001-12-31', 'männlich', 'D', '0786-7296', TRUE, '2026-01-09', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0786-7296'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2026-01-09', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 42. Thiede, Lennart Leander ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Lennart Leander', 'Thiede', '2004-08-27', 'männlich', 'D', '0260-0890', TRUE, '2025-05-21', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0260-0890'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-05-21', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 43. Tielmann, Jonas Louis ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Jonas Louis', 'Tielmann', '2004-10-03', 'männlich', 'D', '0762-0772', TRUE, '2025-06-12', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0762-0772'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-06-12', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 44. von Corvin-Wiersbitzki, Pepe (shared with 1.Hr) ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Pepe', 'von Corvin-Wiersbitzki', '2004-09-21', 'männlich', 'D', '0239-8874', TRUE, '2025-06-05', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0239-8874'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-06-05', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 45. Waap, Victor ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Victor', 'Waap', '2002-08-29', 'männlich', 'RU', '0302-2738', TRUE, '2026-09-02', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0302-2738'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2026-09-02', '2026-09-20')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 46. Weidner, Julius Jonas (no Spielrecht dates) ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Julius Jonas', 'Weidner', '2003-07-11', 'männlich', 'D', '0196-8076', TRUE, CURRENT_DATE, v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0196-8076'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 47. Weise, Ben Moritz ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Ben Moritz', 'Weise', '2004-04-18', 'männlich', 'D', '0228-5299', TRUE, '2025-06-27', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0228-5299'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-06-27', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 48. Wisniewski, Jordi Noah ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Jordi Noah', 'Wisniewski', '2005-07-26', 'männlich', 'D', '0203-3515', TRUE, '2025-09-11', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0203-3515'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-09-11', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    RAISE NOTICE 'Migration 016 complete: 3.Herren — 48 players + 1 Teamoffizieller (Bintz) imported into team %', v_team_id;
END $$;
