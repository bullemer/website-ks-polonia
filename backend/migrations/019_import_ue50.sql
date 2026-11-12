-- Migration 019: Import Polonia 1.Ü50 roster
-- Team: Polonia 1.Ü50 | Bezirksliga | Herren Ü50
-- DFB Vereinsnummer: 03000208
-- 18 players + 2 Teamoffizielle (Ziolkowski, Kania — both also players)
-- Many shared with Ü40: Fendryk, Fiedziuszko, Jackiewicz, Janiszek, Kardys, Kunkel, Nowak, Pol

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
    VALUES ('Polonia 1.Ü50', 'Herren Ü50', 'Bezirksliga', v_div_id, '03000208', TRUE, 60)
    ON CONFLICT DO NOTHING
    RETURNING id INTO v_team_id;
    IF v_team_id IS NULL THEN
        SELECT id INTO v_team_id FROM teams WHERE mannschaftsname = 'Polonia 1.Ü50';
    END IF;
    IF v_team_id IS NULL THEN
        RAISE EXCEPTION 'Could not create or find 1.Ü50 team';
    ELSE
        RAISE NOTICE 'Using 1.Ü50 team with id %', v_team_id;
    END IF;

    -- ═══════════════════════════════════════
    --  PLAYERS (18)
    -- ═══════════════════════════════════════

    -- ─── 1. Fendryk, Marcin (shared with Ü40) ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Marcin', 'Fendryk', '1980-03-23', 'männlich', 'PL', '0503-7524', TRUE, '2017-07-20', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0503-7524'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2017-07-20', '2026-08-30')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 2. Fiedziuszko, Wojciech (shared with 4.Hr, Ü40) ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Wojciech', 'Fiedziuszko', '1975-07-09', 'männlich', 'PL', '0761-1952', TRUE, '2025-06-04', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0761-1952'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-06-04', '2026-08-30')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 3. Gasowski, Krzysztof Jaroslaw ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Krzysztof Jaroslaw', 'Gasowski', '1967-02-27', 'männlich', 'PL', '0680-4904', TRUE, '2023-05-04', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0680-4904'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2023-05-04', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 4. Ginter, Adam Pawel ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Adam Pawel', 'Ginter', '1972-09-30', 'männlich', 'PL', '0016-4284', TRUE, '2026-11-11', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0016-4284'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2026-11-11', '2026-11-12')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 5. Jackiewicz, Wojciech (shared with Ü40) ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Wojciech', 'Jackiewicz', '1970-12-17', 'männlich', 'PL', '0574-4903', TRUE, '2019-09-30', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0574-4903'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2019-09-30', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 6. Janiszek, Waldemar (shared with Ü40) ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Waldemar', 'Janiszek', '1967-12-22', 'männlich', 'PL', '0637-7249', TRUE, '2022-03-29', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0637-7249'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2022-03-29', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 7. Kana, Miroslav (SLO → SI) ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Miroslav', 'Kana', '1974-08-21', 'männlich', 'SI', '0260-9597', TRUE, '2018-03-23', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0260-9597'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2018-03-23', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 8. Kania, Tomasz Mieczyslaw — Teamoffizieller ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, strasse, plz, ort, is_active, eintrittsdatum, claim_token)
    VALUES ('Tomasz Mieczyslaw', 'Kania', '1974-12-29', 'männlich', 'D', '157306', 'Finkenau 38', '22081', 'Hamburg', TRUE, '2005-02-12', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  strasse = EXCLUDED.strasse, plz = EXCLUDED.plz, ort = EXCLUDED.ort,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '157306'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'teamoffizieller', 'active', '2005-02-12', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET role = 'teamoffizieller', spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 9. Kardys, Adam Tomasz (shared with Ü40) ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Adam Tomasz', 'Kardys', '1975-08-20', 'männlich', 'PL', '0662-5974', TRUE, '2022-09-28', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0662-5974'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2022-09-28', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 10. Klose, Erhard ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Erhard', 'Klose', '1957-05-12', 'männlich', 'D', '4757', TRUE, '1988-06-10', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '4757'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '1988-06-10', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 11. Kunkel, Przemyslaw Sebastian (shared with 4.Hr, Ü40) ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Przemyslaw Sebastian', 'Kunkel', '1978-09-03', 'männlich', 'PL', '0760-9921', TRUE, '2025-06-02', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0760-9921'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2025-06-02', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 12. Nowak, Arkadiusz Jerzy (shared with Ü40) ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Arkadiusz Jerzy', 'Nowak', '1976-10-01', 'männlich', 'PL', '0508-0701', TRUE, '2017-07-20', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0508-0701'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2017-07-20', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 13. Patalan, Krzysztof ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Krzysztof', 'Patalan', '1972-08-13', 'männlich', 'PL', '0494-5800', TRUE, '2019-09-08', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0494-5800'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2019-09-08', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 14. Pol, Tomasz Leslaw (shared with Ü40) ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Tomasz Leslaw', 'Pol', '1973-09-14', 'männlich', 'PL', '0298-7039', TRUE, '2012-02-08', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0298-7039'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2012-02-08', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 15. Pomykajczyk, Krzysztof Jan ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Krzysztof Jan', 'Pomykajczyk', '1976-01-09', 'männlich', 'PL', '0707-9222', TRUE, '2023-11-14', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0707-9222'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2023-11-14', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 16. Sionek, Tomasz ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Tomasz', 'Sionek', '1965-09-17', 'männlich', 'D', '0357-3774', TRUE, '2013-08-22', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '0357-3774'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2013-08-22', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 17. Stepniak, Peter ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, is_active, eintrittsdatum, claim_token)
    VALUES ('Peter', 'Stepniak', '1968-01-27', 'männlich', 'D', '24025', TRUE, '2003-10-08', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '24025'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'player', 'active', '2003-10-08', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    -- ─── 18. Ziolkowski, Janusz — Teamoffizieller ───
    v_token := md5(random()::text || clock_timestamp()::text || random()::text);
    INSERT INTO members (vorname, nachname, geburtsdatum, geschlecht, nationality, passnummer, strasse, plz, ort, is_active, eintrittsdatum, claim_token)
    VALUES ('Janusz', 'Ziolkowski', '1967-03-05', 'männlich', 'D', '138170', 'Finkenau 38', '22081', 'Hamburg', TRUE, '2002-07-12', v_token)
    ON CONFLICT (passnummer) WHERE passnummer IS NOT NULL AND passnummer != ''
    DO UPDATE SET nationality = EXCLUDED.nationality, geschlecht = EXCLUDED.geschlecht,
                  strasse = EXCLUDED.strasse, plz = EXCLUDED.plz, ort = EXCLUDED.ort,
                  claim_token = CASE WHEN members.email IS NULL THEN EXCLUDED.claim_token ELSE members.claim_token END
    RETURNING id INTO v_member_id;
    IF v_member_id IS NULL THEN SELECT id INTO v_member_id FROM members WHERE passnummer = '138170'; END IF;
    INSERT INTO member_divisions (member_id, division_id, status) VALUES (v_member_id, v_div_id, 'active') ON CONFLICT (member_id, division_id) DO NOTHING;
    INSERT INTO member_teams (member_id, team_id, role, status, spielrecht_ab, dfb_registered_at)
    VALUES (v_member_id, v_team_id, 'teamoffizieller', 'active', '2002-07-12', '2026-05-31')
    ON CONFLICT (member_id, team_id) DO UPDATE SET role = 'teamoffizieller', spielrecht_ab = EXCLUDED.spielrecht_ab, dfb_registered_at = EXCLUDED.dfb_registered_at;

    RAISE NOTICE 'Migration 019 complete: 1.Ü50 — 18 players + 2 Teamoffizielle (Ziolkowski, Kania) imported into team %', v_team_id;
END $$;
