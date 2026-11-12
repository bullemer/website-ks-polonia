-- Migration 018: Import Polonia 1.Ü40 roster
-- Team: Polonia 1.Ü40 | Landesliga | Herren Ü40
-- DFB Vereinsnummer: 03000208
-- 34 players + 1 Teamoffizieller (Gieros, also a player)
-- Shared: Bondarchuk (2.Hr), Fiedziuszko (4.Hr), Kunkel (4.Hr), Maidan (2.Hr), Nahornyi (2.Hr)

DO $$
DECLARE
    v_div_id    INT;
    v_team_id   INT;
    v_member_id INT;
    v_token     TEXT;
BEGIN
    SELECT id INTO v_div_id FROM divisions WHERE name = 'Fußball' AND is_active = TRUE LIMIT 1;
    IF v_div_id IS NULL THEN RAISE EXCEPTION 'Division fussball not found'; END IF;

    -- ═══════════════════════════════════════
    --  CREATE TEAM
    -- ═══════════════════════════════════════
    INSERT INTO teams (mannschaftsname, mannschaftsart, spielklasse, division_id, dfb_team_id, is_active, sort_order)
    VALUES ('Polonia 1.Ü40', 'Herren Ü40', 'Landesliga', v_div_id, '03000208', TRUE, 50)
    ON CONFLICT DO NOTHING
    RETURNING id INTO v_team_id;
    IF v_team_id IS NULL THEN
        SELECT id INTO v_team_id FROM teams WHERE mannschaftsname = 'Polonia 1.Ü40';
    END IF;
    IF v_team_id IS NULL THEN
        RAISE EXCEPTION 'Could not create or find 1.Ü40 team';
    ELSE
        RAISE NOTICE 'Using 1.Ü40 team with id %', v_team_id;
    END IF;

    -- ═══════════════════════════════════════
    --  PLAYERS (34)
    -- ═══════════════════════════════════════

    -- ─── 1. Bialobrzeski, Lukasz Oktawian ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Lukasz Oktawian', 'Bialobrzeski', '1983-11-07', 'männlich', 'PL', '0706-6717', TRUE, '2023-10-30', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0706-6717'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2023-10-30', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 2. Bondarchuk, Mykhailo (shared with 2.Hr) ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Mykhailo', 'Bondarchuk', '1987-11-11', 'männlich', 'UA', '0763-2018', TRUE, '2025-06-25', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0763-2018'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-06-25', '2026-09-25')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 3. Dygowski, Piotr Maciej ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Piotr Maciej', 'Dygowski', '1982-03-09', 'männlich', 'PL', '0662-5973', TRUE, '2022-09-28', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0662-5973'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2022-09-28', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 4. Fendryk, Marcin ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Marcin', 'Fendryk', '1980-03-23', 'männlich', 'PL', '0503-7524', TRUE, '2017-07-20', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0503-7524'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2017-07-20', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 5. Fiedziuszko, Wojciech (shared with 4.Hr) ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Wojciech', 'Fiedziuszko', '1975-07-09', 'männlich', 'PL', '0761-1952', TRUE, '2025-06-04', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0761-1952'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-06-04', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 6. Gieros, Marek — Teamoffizieller ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, email, strasse, plz, ort, is_active, eintrittsdatum, claim_token)
    VALUES ('Marek', 'Gieros', '1980-12-18', 'männlich', 'PL', '0446-7231', 'mgieros@gmail.com', 'Finkenau', '22081', 'Hamburg', TRUE, '2015-09-28', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  email = COALESCE(EXCLUDED.email, members.email),
                  strasse = EXCLUDED.strasse, plz = EXCLUDED.plz, ort = EXCLUDED.ort,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0446-7231'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'teamoffizieller', 'active', '2015-09-28', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET role = 'teamoffizieller', spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 7. Jackiewicz, Wojciech ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Wojciech', 'Jackiewicz', '1970-12-17', 'männlich', 'PL', '0574-4903', TRUE, '2019-09-30', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0574-4903'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2019-09-30', '2026-08-13')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 8. Jackow, Piotr Wacław ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Piotr Wacław', 'Jackow', '1987-02-21', 'männlich', 'PL', '0801-4963', TRUE, '2026-07-10', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0801-4963'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2026-07-10', '2026-08-13')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 9. Janiszek, Waldemar ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Waldemar', 'Janiszek', '1967-12-22', 'männlich', 'PL', '0637-7249', TRUE, '2022-03-29', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0637-7249'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2022-03-29', '2026-08-13')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 10. Kardys, Adam Tomasz ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Adam Tomasz', 'Kardys', '1975-08-20', 'männlich', 'PL', '0662-5974', TRUE, '2022-09-28', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0662-5974'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2022-09-28', '2026-10-02')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 11. Kempa, Sebastian Piotr ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Sebastian Piotr', 'Kempa', '1986-02-20', 'männlich', 'PL', '0471-8065', TRUE, '2016-08-10', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0471-8065'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2016-08-10', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 12. Kleina, Sebastian Bogumil ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Sebastian Bogumil', 'Kleina', '1980-07-27', 'männlich', 'D', '0653-0226', TRUE, '2022-08-18', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0653-0226'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2022-08-18', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 13. Krzysztofik, Piotr Jerzy ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Piotr Jerzy', 'Krzysztofik', '1985-11-01', 'männlich', 'PL', '0677-3326', TRUE, '2023-03-28', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0677-3326'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2023-03-28', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 14. Krzywinski, Kacper Jozef ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Kacper Jozef', 'Krzywinski', '1988-07-07', 'männlich', 'D', '0184-8614', TRUE, '2026-08-31', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0184-8614'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2026-08-31', '2026-08-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 15. Kunkel, Przemyslaw Sebastian (shared with 4.Hr) ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Przemyslaw Sebastian', 'Kunkel', '1978-09-03', 'männlich', 'PL', '0760-9921', TRUE, '2025-06-02', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0760-9921'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-06-02', '2026-08-16')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 16. Lembowicz, Marcin Maciej ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Marcin Maciej', 'Lembowicz', '1984-09-11', 'männlich', 'PL', '0669-6417', TRUE, '2022-12-12', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0669-6417'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2022-12-12', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 17. Lopuszanski, Maciej Krzysztof ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Maciej Krzysztof', 'Lopuszanski', '1984-08-16', 'männlich', 'PL', '0438-7449', TRUE, '2015-08-13', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0438-7449'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2015-08-13', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 18. Maćkowiak, Robert ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Robert', 'Maćkowiak', '1985-07-09', 'männlich', 'PL', '0730-7881', TRUE, '2024-08-16', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0730-7881'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2024-08-16', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 19. Maidan, Ruslan (shared with 2.Hr) ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Ruslan', 'Maidan', '1989-09-25', 'männlich', 'UA', '0688-0300', TRUE, '2026-02-27', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0688-0300'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2026-02-27', '2026-10-02')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 20. Makarowski, Piotr ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Piotr', 'Makarowski', '1980-08-12', 'männlich', 'PL', '0718-3175', TRUE, '2024-04-21', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0718-3175'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2024-04-21', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 21. Nahornyi, Mykola (shared with 2.Hr) ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Mykola', 'Nahornyi', '1987-05-08', 'männlich', 'UA', '0765-3456', TRUE, '2025-07-10', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0765-3456'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-07-10', '2026-09-25')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 22. Nowak, Arkadiusz Jerzy ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Arkadiusz Jerzy', 'Nowak', '1976-10-01', 'männlich', 'PL', '0508-0701', TRUE, '2017-07-20', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0508-0701'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2017-07-20', '2026-08-13')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 23. Nowak, Marcin ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Marcin', 'Nowak', '1982-11-27', 'männlich', 'PL', '0692-5744', TRUE, '2023-08-17', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0692-5744'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2023-08-17', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 24. Obertowski, Dawid ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Dawid', 'Obertowski', '1986-11-19', 'männlich', 'PL', '0739-9857', TRUE, '2024-09-24', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0739-9857'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2024-09-24', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 25. Pacha, Milosz Pawel ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Milosz Pawel', 'Pacha', '1987-01-25', 'männlich', 'PL', '0651-6443', TRUE, '2022-08-10', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0651-6443'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2022-08-10', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 26. Pol, Tomasz Leslaw ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Tomasz Leslaw', 'Pol', '1973-09-14', 'männlich', 'PL', '0298-7039', TRUE, '2012-02-08', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0298-7039'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2012-02-08', '2026-08-13')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 27. Ratajczak, Przemysław Krzysztof ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Przemysław Krzysztof', 'Ratajczak', '1988-02-27', 'männlich', 'PL', '0802-4514', TRUE, '2026-07-17', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0802-4514'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2026-07-17', '2026-07-19')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 28. Rekowski, Tomasz ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Tomasz', 'Rekowski', '1987-03-09', 'männlich', 'PL', '0717-2767', TRUE, '2024-04-09', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0717-2767'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2024-04-09', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 29. Schleicher, Mateusz ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Mateusz', 'Schleicher', '1988-03-22', 'männlich', 'D', '0077-0056', TRUE, '2025-04-27', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0077-0056'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-04-27', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 30. Sendor, Tomasz Maciej ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Tomasz Maciej', 'Sendor', '1988-02-16', 'männlich', 'PL', '0554-2147', TRUE, '2024-09-01', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0554-2147'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2024-09-01', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 31. Spon, Miroslaw ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Miroslaw', 'Spon', '1980-12-03', 'männlich', 'D', '0705-8845', TRUE, '2023-10-23', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0705-8845'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2023-10-23', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 32. Strugala, Grzegorz Antoni ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Grzegorz Antoni', 'Strugala', '1984-09-02', 'männlich', 'PL', '0680-2871', TRUE, '2023-05-03', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0680-2871'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2023-05-03', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 33. Supruniuk, Serhii ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Serhii', 'Supruniuk', '1984-07-09', 'männlich', 'UA', '0752-9703', TRUE, '2025-02-26', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0752-9703'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-02-26', '2026-09-25')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 34. Wawrowski, Patryk ───
    v_token := encode(gen_random_bytes(32), 'hex');
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Patryk', 'Wawrowski', '1982-03-23', 'männlich', 'D', '74272', TRUE, '1998-08-25', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '74272'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '1998-08-25', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    RAISE NOTICE 'Migration 018 complete: 1.Ü40 — 34 players + 1 Teamoffizieller (Gieros) imported into team %', v_team_id;
END $$;
