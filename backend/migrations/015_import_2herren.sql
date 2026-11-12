-- ============================================================
-- Migration 015: Import 2.Herren team roster + Trainer
--
-- Team: Polonia 2.Hr. | Kreisklasse | Herren
-- 25 players + 1 Trainer (Chernialis, who is also a player)
-- ============================================================

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

    -- Find or create the 2.Herren team
    SELECT id INTO v_team_id
    FROM teams
    WHERE mannschaftsname ILIKE '%2.Hr%' OR mannschaftsname ILIKE '%2.Herren%'
      AND is_active = TRUE
      AND division_id = v_div_id
    LIMIT 1;

    IF v_team_id IS NULL THEN
        INSERT INTO teams (
            nummer, vereinsname, mannschaftsart, mannschaftsname, spielklasse,
            status, division_id, is_active, sort_order
        ) VALUES (
            '2.Hr', 'KS Polonia Hamburg', 'Herren', 'Polonia 2.Herren', 'Kreisklasse',
            'aktiv', v_div_id, TRUE, 2
        )
        RETURNING id INTO v_team_id;
        RAISE NOTICE 'Created 2.Herren team with id %', v_team_id;
    ELSE
        RAISE NOTICE 'Using existing 2.Herren team with id %', v_team_id;
    END IF;

    -- ═══════════════════════════════════════
    --  PLAYERS (25) — Chernialis gets role='trainer'
    -- ═══════════════════════════════════════

    -- ─── 1. Baldyniuk, Andrii ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Andrii', 'Baldyniuk', '1998-11-09', 'männlich', 'UA', '0691-6078', TRUE, '2026-02-21', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0691-6078'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2026-02-21', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 2. Barbash, Oleksii ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Oleksii', 'Barbash', '1995-08-01', 'männlich', 'UA', '0765-1717', TRUE, '2025-07-09', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0765-1717'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-07-09', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 3. Basarab, Dmytro ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Dmytro', 'Basarab', '2005-11-14', 'männlich', 'UA', '0740-9683', TRUE, '2026-08-16', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0740-9683'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2026-08-16', '2026-08-17')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 4. Bondarchuk, Mykhailo ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Mykhailo', 'Bondarchuk', '1987-11-11', 'männlich', 'UA', '0763-2018', TRUE, '2025-06-25', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0763-2018'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-06-25', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 5. Bondarenko, Maksym ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Maksym', 'Bondarenko', '2007-10-01', 'männlich', 'UA', '0789-2070', TRUE, '2026-02-23', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0789-2070'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2026-02-23', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 6. Buchii, Taras ───
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
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-06-29', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 7. Chernialis, Oleksandr (Trainer + Spieler) ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, strasse, plz, ort, is_active, eintrittsdatum, claim_token)
    VALUES ('Oleksandr', 'Chernialis', '1993-02-22', 'männlich', 'UA', '0646-9335', 'Finkenau', '22081', 'Hamburg', TRUE, '2022-07-05', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  strasse = EXCLUDED.strasse, plz = EXCLUDED.plz, ort = EXCLUDED.ort,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0646-9335'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    -- Role = trainer (he's both trainer and player; trainer takes precedence)
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at, joined_at)
    VALUES (v_member_id, v_team_id, 'trainer', 'active', '2022-07-05', '2026-05-31', '2025-05-18')
    ON CONFLICT (member_id, team_id) DO UPDATE SET role = 'trainer', spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;
    RAISE NOTICE 'Added Oleksandr Chernialis (%) as Trainer + Spieler → 2.Herren', v_member_id;

    -- ─── 8. Dvirnyk, Oleksii ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Oleksii', 'Dvirnyk', '1994-06-15', 'männlich', 'UA', '0763-2020', TRUE, '2025-06-25', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0763-2020'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-06-25', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 9. Kachurovskyi, Vladyslav ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Vladyslav', 'Kachurovskyi', '1999-01-09', 'männlich', 'UA', '0765-1616', TRUE, '2025-07-09', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0765-1616'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-07-09', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 10. Lashchenko, Dmytro ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Dmytro', 'Lashchenko', '1995-11-06', 'männlich', 'UA', '0808-9437', TRUE, '2026-08-27', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0808-9437'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2026-08-27', '2026-08-28')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 11. Lemak, Mykhailo ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Mykhailo', 'Lemak', '1993-12-17', 'männlich', 'UA', '0766-3673', TRUE, '2025-07-17', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0766-3673'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-07-17', '2026-08-08')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 12. Mai, Valentin ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Valentin', 'Mai', '1988-12-11', 'männlich', 'D', '0132-3634', TRUE, '2024-06-30', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0132-3634'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2024-06-30', '2026-08-08')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 13. Maidan, Ruslan ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Ruslan', 'Maidan', '1989-09-25', 'männlich', 'UA', '0688-0300', TRUE, '2026-02-27', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0688-0300'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2026-02-27', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 14. Marushka, Ruslan ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Ruslan', 'Marushka', '1998-08-23', 'männlich', 'UA', '0665-8761', TRUE, '2026-02-21', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0665-8761'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2026-02-21', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 15. Nahornyi, Mykola ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Mykola', 'Nahornyi', '1987-05-08', 'männlich', 'UA', '0765-3456', TRUE, '2025-07-10', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0765-3456'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-07-10', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 16. Nai, Andrii ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Andrii', 'Nai', '1992-01-09', 'männlich', 'UA', '0756-4509', TRUE, '2025-04-04', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0756-4509'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-04-04', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 17. Nika, Kristi ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Kristi', 'Nika', '1999-01-06', 'männlich', 'AL', '0775-6535', TRUE, '2025-09-13', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0775-6535'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-09-13', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 18. Pishchulin, Oleksander ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Oleksander', 'Pishchulin', '1992-03-03', 'männlich', 'UA', '0756-4507', TRUE, '2025-04-04', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0756-4507'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-04-04', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 19. Rodionov, Denys ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Denys', 'Rodionov', '1997-10-30', 'männlich', 'UA', '0766-2235', TRUE, '2025-07-16', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0766-2235'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-07-16', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 20. Rusanenko, Roman ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Roman', 'Rusanenko', '1995-06-16', 'männlich', 'UA', '0766-2135', TRUE, '2025-07-16', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0766-2135'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-07-16', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 21. Shevchuk, Andrii ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Andrii', 'Shevchuk', '1995-02-28', 'männlich', 'UA', '0756-4510', TRUE, '2025-07-06', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0756-4510'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-07-06', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 22. Stepaniuk, Yurii ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Yurii', 'Stepaniuk', '1990-05-07', 'männlich', 'UA', '0794-0339', TRUE, '2026-04-24', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0794-0339'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2026-04-24', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 23. Supruniuk, Serhii ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Serhii', 'Supruniuk', '1984-07-09', 'männlich', 'UA', '0752-9703', TRUE, '2025-02-26', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0752-9703'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-02-26', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 24. Yasenytskyi, Vitalii ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Vitalii', 'Yasenytskyi', '2001-06-24', 'männlich', 'UA', '0806-5618', TRUE, '2026-08-17', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0806-5618'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2026-08-17', '2026-08-18')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 25. Yurko, Oleh ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Oleh', 'Yurko', '1998-04-02', 'männlich', 'UA', '0649-4695', TRUE, '2024-06-27', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0649-4695'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2024-06-27', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    RAISE NOTICE 'Migration 015 complete: 2.Herren — 1 Trainer + 25 players (incl. playing trainer) into team %', v_team_id;
END $$;
