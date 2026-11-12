-- ============================================================
-- Migration 013: Create 1.C-Junioren team, import 10 players,
--                add 'teamoffizieller' role + 3 Team Officials
--
-- Teams affected:
--   - 1.C-Junioren (created here, 10 players imported)
--   - 2.C-Junioren (dfb_team_id 03000208, existing)
--   - E-Junioren (existing)
--
-- Teamoffizielle:
--   1. Tengiz Dadiani    → 1.C-Junioren + 2.C-Junioren
--   2. Artem Churilov    → 2.C-Junioren
--   3. Carsten Bullemer  → E-Junioren
-- ============================================================

DO $$
DECLARE
    v_team_1c    INT;
    v_team_2c    INT;
    v_team_e     INT;
    v_div_id     INT;
    v_member_id  INT;
    v_token      VARCHAR(100);
BEGIN
    -- Find the Fußball division
    SELECT id INTO v_div_id
    FROM divisions
    WHERE name = 'Fußball' AND is_active = TRUE
    LIMIT 1;

    IF v_div_id IS NULL THEN
        RAISE EXCEPTION 'Fußball division not found';
    END IF;

    -- ═══════════════════════════════════════
    --  Find / create teams
    -- ═══════════════════════════════════════

    -- 2.C-Junioren (DFB team ID 03000208)
    SELECT id INTO v_team_2c
    FROM teams
    WHERE dfb_team_id = '03000208' AND is_active = TRUE
    LIMIT 1;

    IF v_team_2c IS NULL THEN
        RAISE EXCEPTION 'Team 2.C-Junioren (dfb_team_id 03000208) not found. Run migration 012 first.';
    END IF;

    -- 1.C-Junioren — create if it doesn't exist
    SELECT id INTO v_team_1c
    FROM teams
    WHERE mannschaftsname ILIKE '%1.C%'
      AND is_active = TRUE
    LIMIT 1;

    IF v_team_1c IS NULL THEN
        INSERT INTO teams (
            nummer, vereinsname, mannschaftsart, mannschaftsname, spielklasse,
            status, division_id, is_active, sort_order
        ) VALUES (
            '1.C', 'KS Polonia Hamburg', 'C-Junioren (A1) 7er', 'Polonia 1.C-Junioren', 'Kreisklasse',
            'aktiv', v_div_id, TRUE, 2
        )
        RETURNING id INTO v_team_1c;
        RAISE NOTICE 'Created 1.C-Junioren team with id %', v_team_1c;
    ELSE
        RAISE NOTICE 'Using existing 1.C-Junioren team with id %', v_team_1c;
    END IF;

    -- E-Junioren
    SELECT id INTO v_team_e
    FROM teams
    WHERE (mannschaftsname ILIKE '%1.E%' OR mannschaftsname ILIKE '%E-Junioren%')
      AND is_active = TRUE
    LIMIT 1;

    IF v_team_e IS NULL THEN
        RAISE EXCEPTION 'Team E-Junioren not found in teams table.';
    END IF;

    RAISE NOTICE 'Teams: 1.C=%, 2.C=%, E=%', v_team_1c, v_team_2c, v_team_e;

    -- ═══════════════════════════════════════
    --  IMPORT 1.C-JUNIOREN PLAYERS (10)
    -- ═══════════════════════════════════════

    -- ─── 1. Barakhovskyi, Ruslan ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Ruslan', 'Barakhovskyi', '2013-08-06', 'männlich', 'UA', '0709-6973', TRUE, '2023-12-12', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0709-6973'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_1c, 'player', 'active', '2023-12-12', '2026-09-12')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 2. Dadiani, Damir ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Damir', 'Dadiani', '2013-09-17', 'männlich', 'UA', '0718-9643', TRUE, '2024-04-29', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0718-9643'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_1c, 'player', 'active', '2024-04-29', '2026-07-12')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 3. Hryshchenko, Pavlo ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Pavlo', 'Hryshchenko', '2012-07-11', 'männlich', 'UA', '0678-7632', TRUE, '2023-04-17', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0678-7632'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_1c, 'player', 'active', '2023-04-17', '2026-07-12')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 4. Israielian, Tihran ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Tihran', 'Israielian', '2013-05-30', 'männlich', 'UA', '0643-1556', TRUE, '2022-05-25', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0643-1556'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_1c, 'player', 'active', '2022-05-25', '2026-09-19')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 5. Martyniuk, Illia ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Illia', 'Martyniuk', '2012-08-07', 'männlich', 'UA', '0655-4838', TRUE, '2022-08-30', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0655-4838'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_1c, 'player', 'active', '2022-08-30', '2026-07-12')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 6. Nezhyvyi, Davyd ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Davyd', 'Nezhyvyi', '2012-11-29', 'männlich', 'UA', '0661-6313', TRUE, '2022-09-21', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0661-6313'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_1c, 'player', 'active', '2022-09-21', '2026-07-12')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 7. Pinchuk, Mykyta ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Mykyta', 'Pinchuk', '2013-03-20', 'männlich', 'UA', '0643-1398', TRUE, '2022-05-25', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0643-1398'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_1c, 'player', 'active', '2022-05-25', '2026-07-12')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 8. Riznychenko, Mark ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Mark', 'Riznychenko', '2012-07-12', 'männlich', 'UA', '0706-6727', TRUE, '2023-10-27', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0706-6727'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_1c, 'player', 'active', '2023-10-27', '2026-07-12')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 9. Strashko, Kyrylo ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Kyrylo', 'Strashko', '2013-12-17', 'männlich', 'UA', '0685-0430', TRUE, '2023-06-25', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0685-0430'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_1c, 'player', 'active', '2023-06-25', '2026-07-12')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 10. Sukhonosov, Volodymyr ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Volodymyr', 'Sukhonosov', '2012-10-06', 'männlich', 'UA', '0708-6512', TRUE, '2023-11-23', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0708-6512'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_1c, 'player', 'active', '2023-11-23', '2026-07-12')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    RAISE NOTICE 'Imported 10 players into 1.C-Junioren team %', v_team_1c;

    -- ═══════════════════════════════════════
    --  TEAMOFFIZIELLE
    -- ═══════════════════════════════════════

    -- ─── 1. Tengiz Dadiani → 1.C-Junioren + 2.C-Junioren ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (
        vorname, nachname, email, strasse, plz, ort,
        is_active, eintrittsdatum, claim_token
    ) VALUES (
        'Tengiz', 'Dadiani', 'tengizdadiani3@gmail.com',
        'Finkenau 38', '22083', 'Hamburg',
        TRUE, CURRENT_DATE, v_token
    )
    ON CONFLICT (email) WHERE email IS NOT NULL
    DO UPDATE SET
        strasse = EXCLUDED.strasse,
        plz = EXCLUDED.plz,
        ort = EXCLUDED.ort,
        claim_token = CASE WHEN members.password_hash IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;

    IF v_member_id IS NULL THEN
        SELECT id INTO v_member_id FROM members WHERE email = 'tengizdadiani3@gmail.com';
    END IF;

    INSERT INTO member_divisions (member_id, division_id, status)
    VALUES (v_member_id, v_div_id, 'active')
    ON CONFLICT (member_id, division_id) DO NOTHING;

    INSERT INTO member_teams (member_id, team_id, role, status, joined_at)
    VALUES (v_member_id, v_team_1c, 'teamoffizieller', 'active', CURRENT_DATE)
    ON CONFLICT (member_id, team_id)
    DO UPDATE SET role = 'teamoffizieller', status = 'active', left_at = NULL;

    INSERT INTO member_teams (member_id, team_id, role, status, joined_at)
    VALUES (v_member_id, v_team_2c, 'teamoffizieller', 'active', CURRENT_DATE)
    ON CONFLICT (member_id, team_id)
    DO UPDATE SET role = 'teamoffizieller', status = 'active', left_at = NULL;

    RAISE NOTICE 'Added Tengiz Dadiani (%) as Teamoffizieller → 1.C (%) + 2.C (%)', v_member_id, v_team_1c, v_team_2c;

    -- ─── 2. Artem Churilov → 2.C-Junioren ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (
        vorname, nachname, email, strasse, plz, ort,
        is_active, eintrittsdatum, claim_token
    ) VALUES (
        'Artem', 'Churilov', 'coachchuril@gmail.com',
        'Tonndorfer Hauptstraße 87b', '22045', 'Hamburg',
        TRUE, CURRENT_DATE, v_token
    )
    ON CONFLICT (email) WHERE email IS NOT NULL
    DO UPDATE SET
        strasse = EXCLUDED.strasse,
        plz = EXCLUDED.plz,
        ort = EXCLUDED.ort,
        claim_token = CASE WHEN members.password_hash IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;

    IF v_member_id IS NULL THEN
        SELECT id INTO v_member_id FROM members WHERE email = 'coachchuril@gmail.com';
    END IF;

    INSERT INTO member_divisions (member_id, division_id, status)
    VALUES (v_member_id, v_div_id, 'active')
    ON CONFLICT (member_id, division_id) DO NOTHING;

    INSERT INTO member_teams (member_id, team_id, role, status, joined_at)
    VALUES (v_member_id, v_team_2c, 'teamoffizieller', 'active', CURRENT_DATE)
    ON CONFLICT (member_id, team_id)
    DO UPDATE SET role = 'teamoffizieller', status = 'active', left_at = NULL;

    RAISE NOTICE 'Added Artem Churilov (%) as Teamoffizieller → 2.C (%)', v_member_id, v_team_2c;

    -- ─── 3. Carsten Bullemer → E-Junioren ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (
        vorname, nachname, email, strasse, plz, ort,
        is_active, eintrittsdatum, claim_token
    ) VALUES (
        'Carsten', 'Bullemer', 'carsten@navisense.de',
        'Dorothea Bernstein Weg 28', '22081', 'Hamburg',
        TRUE, CURRENT_DATE, v_token
    )
    ON CONFLICT (email) WHERE email IS NOT NULL
    DO UPDATE SET
        strasse = EXCLUDED.strasse,
        plz = EXCLUDED.plz,
        ort = EXCLUDED.ort,
        claim_token = CASE WHEN members.password_hash IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;

    IF v_member_id IS NULL THEN
        SELECT id INTO v_member_id FROM members WHERE email = 'carsten@navisense.de';
    END IF;

    INSERT INTO member_divisions (member_id, division_id, status)
    VALUES (v_member_id, v_div_id, 'active')
    ON CONFLICT (member_id, division_id) DO NOTHING;

    INSERT INTO member_teams (member_id, team_id, role, status, joined_at)
    VALUES (v_member_id, v_team_e, 'teamoffizieller', 'active', CURRENT_DATE)
    ON CONFLICT (member_id, team_id)
    DO UPDATE SET role = 'teamoffizieller', status = 'active', left_at = NULL;

    RAISE NOTICE 'Added Carsten Bullemer (%) as Teamoffizieller → E-Junioren (%)', v_member_id, v_team_e;

    RAISE NOTICE 'Migration 013 complete: 1.C-Junioren team created, 10 players imported, 3 Teamoffizielle (4 assignments).';
END $$;
