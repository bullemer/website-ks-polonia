-- ============================================================
-- Migration 012: Add dfb_team_id to teams + Import 2.C-Junioren
-- Creates the 2.C-Junioren team and imports 11 players from
-- the fussball.de Spielberechtigungsliste.
-- ============================================================

-- 1. Add DFB team identifier to teams table
ALTER TABLE teams ADD COLUMN IF NOT EXISTS dfb_team_id VARCHAR(20);

-- 2. Set dfb_team_id for E-Junioren (if known)
-- UPDATE teams SET dfb_team_id = '...' WHERE mannschaftsname ILIKE '%1.E%';

DO $$
DECLARE
    v_team_id    INT;
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

    -- Create the 2.C-Junioren team if it doesn't exist
    SELECT id INTO v_team_id
    FROM teams
    WHERE mannschaftsname ILIKE '%2.C%'
      AND is_active = TRUE
    LIMIT 1;

    IF v_team_id IS NULL THEN
        INSERT INTO teams (
            nummer, vereinsname, mannschaftsart, mannschaftsname, spielklasse,
            status, division_id, is_active, sort_order, dfb_team_id
        ) VALUES (
            '2.C', 'KS Polonia Hamburg', 'C-Junioren (J1) 7er', 'Polonia 2.C-Junioren', 'Kreisklasse',
            'aktiv', v_div_id, TRUE, 3, '03000208'
        )
        RETURNING id INTO v_team_id;
        RAISE NOTICE 'Created 2.C-Junioren team with id %', v_team_id;
    ELSE
        -- Update dfb_team_id if not set
        UPDATE teams SET dfb_team_id = '03000208' WHERE id = v_team_id AND dfb_team_id IS NULL;
        RAISE NOTICE 'Using existing 2.C-Junioren team with id %', v_team_id;
    END IF;

    RAISE NOTICE 'Importing 2.C-Junioren players into team % (division %)', v_team_id, v_div_id;

    -- ─── 1. Bakai, Yan ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Yan', 'Bakai', '2015-07-21', 'männlich', 'UA', '0644-3723', TRUE, '2022-06-13', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0644-3723'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2022-06-13', '2026-07-12')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 2. Goloborodko, Vladyslav ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Vladyslav', 'Goloborodko', '2014-04-06', 'männlich', 'UA', '0720-7401', TRUE, '2024-05-24', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0720-7401'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2024-05-24', '2026-07-12')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 3. Hraivoronskyi, Sviatoslav ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Sviatoslav', 'Hraivoronskyi', '2015-03-24', 'männlich', 'UA', '0751-6437', TRUE, '2025-07-05', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0751-6437'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-07-05', '2026-07-12')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 4. Karpenko, Artem ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Artem', 'Karpenko', '2014-06-08', 'männlich', 'UA', '0819-7413', TRUE, '2026-10-15', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0819-7413'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2026-10-15', '2026-10-16')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 5. Kozarenko, Nazar ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Nazar', 'Kozarenko', '2014-03-30', 'männlich', 'UA', '0684-0336', TRUE, '2023-06-15', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0684-0336'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2023-06-15', '2026-07-12')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 6. Kviatkovskyi, Viacheslav ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Viacheslav', 'Kviatkovskyi', '2013-12-20', 'männlich', 'UA', '0717-7668', TRUE, '2024-04-15', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0717-7668'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2024-04-15', '2026-07-12')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 7. Pakhomov, Kostiantyn ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Kostiantyn', 'Pakhomov', '2014-09-19', 'männlich', 'UA', '0644-3701', TRUE, '2022-06-13', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0644-3701'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2022-06-13', '2026-07-12')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 8. Rybalka, Kyrylo ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Kyrylo', 'Rybalka', '2013-01-16', 'männlich', 'UA', '0712-9058', TRUE, '2024-02-12', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0712-9058'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2024-02-12', '2026-07-12')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 9. Tielitsyn, Ivan ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Ivan', 'Tielitsyn', '2015-02-09', 'männlich', 'UA', '0673-9679', TRUE, '2023-02-22', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0673-9679'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2023-02-22', '2026-07-12')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 10. Vynohorodskyi, Davyd ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Davyd', 'Vynohorodskyi', '2013-07-05', 'männlich', 'UA', '0812-1077', TRUE, '2026-09-11', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0812-1077'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2026-09-11', '2026-09-15')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 11. Yermolaiev, Maksym ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Maksym', 'Yermolaiev', '2015-07-15', 'männlich', 'UA', '0821-7353', TRUE, '2026-11-03', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0821-7353'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2026-11-03', '2026-11-05')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    RAISE NOTICE 'Successfully imported 11 2.C-Junioren players into team %', v_team_id;
END $$;
