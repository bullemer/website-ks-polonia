-- ============================================================
-- Migration 021: Update 1.E-Jun roster
-- Remove Monroy Metzler and Ulumaskan (no longer on team)
-- Update spielrecht dates for remaining players
-- ============================================================

DO $$
DECLARE
    v_team_id INT;
    v_member_id INT;
BEGIN
    -- Find the E-Junioren team
    SELECT t.id INTO v_team_id
    FROM teams t
    JOIN divisions d ON d.id = t.division_id
    WHERE t.mannschaftsname ILIKE '%E-Jun%'
      AND t.is_active = TRUE
    LIMIT 1;

    IF v_team_id IS NULL THEN
        RAISE NOTICE 'E-Junioren team not found, skipping';
        RETURN;
    END IF;

    -- Deactivate Monroy Metzler, Alexander (0773-3250)
    SELECT id INTO v_member_id FROM members WHERE passnummer = '0773-3250';
    IF v_member_id IS NOT NULL THEN
        UPDATE member_teams SET status = 'inactive', left_at = CURRENT_DATE
        WHERE member_id = v_member_id AND team_id = v_team_id;
        RAISE NOTICE 'Deactivated Monroy Metzler from E-Jun';
    END IF;

    -- Deactivate Ulumaskan, Enes (0791-9702)
    SELECT id INTO v_member_id FROM members WHERE passnummer = '0791-9702';
    IF v_member_id IS NOT NULL THEN
        UPDATE member_teams SET status = 'inactive', left_at = CURRENT_DATE
        WHERE member_id = v_member_id AND team_id = v_team_id;
        RAISE NOTICE 'Deactivated Ulumaskan from E-Jun';
    END IF;

    -- Update spielrecht/registration dates for current roster
    UPDATE member_teams SET spielrecht_ab = '2026-03-03', dfb_registered_at = '2026-07-26'
    WHERE team_id = v_team_id AND member_id = (SELECT id FROM members WHERE passnummer = '0695-8073'); -- Bajster

    UPDATE member_teams SET spielrecht_ab = '2023-01-30', dfb_registered_at = '2026-07-26'
    WHERE team_id = v_team_id AND member_id = (SELECT id FROM members WHERE passnummer = '0672-0157'); -- Bullemer

    UPDATE member_teams SET spielrecht_ab = '2024-08-14', dfb_registered_at = '2026-07-26'
    WHERE team_id = v_team_id AND member_id = (SELECT id FROM members WHERE passnummer = '0730-3584'); -- Dygowski

    UPDATE member_teams SET spielrecht_ab = '2025-01-11', dfb_registered_at = '2026-07-26'
    WHERE team_id = v_team_id AND member_id = (SELECT id FROM members WHERE passnummer = '0749-8931'); -- Grunenberg

    UPDATE member_teams SET spielrecht_ab = '2025-01-01', dfb_registered_at = '2026-07-26'
    WHERE team_id = v_team_id AND member_id = (SELECT id FROM members WHERE passnummer = '0749-3470'); -- Kumara

    UPDATE member_teams SET spielrecht_ab = '2023-10-25', dfb_registered_at = '2026-07-26'
    WHERE team_id = v_team_id AND member_id = (SELECT id FROM members WHERE passnummer = '0706-1082'); -- Lababidi

    UPDATE member_teams SET spielrecht_ab = '2025-01-05', dfb_registered_at = '2026-07-26'
    WHERE team_id = v_team_id AND member_id = (SELECT id FROM members WHERE passnummer = '0749-3603'); -- Lescale

    UPDATE member_teams SET spielrecht_ab = '2025-01-01', dfb_registered_at = '2026-07-26'
    WHERE team_id = v_team_id AND member_id = (SELECT id FROM members WHERE passnummer = '0749-3472'); -- Onuorah

    UPDATE member_teams SET spielrecht_ab = '2025-09-12', dfb_registered_at = '2026-07-26'
    WHERE team_id = v_team_id AND member_id = (SELECT id FROM members WHERE passnummer = '0775-6946'); -- Rosenthal

    UPDATE member_teams SET spielrecht_ab = '2026-09-15', dfb_registered_at = '2026-09-17'
    WHERE team_id = v_team_id AND member_id = (SELECT id FROM members WHERE passnummer = '0813-1308'); -- Stumpf

    UPDATE member_teams SET spielrecht_ab = '2025-02-22', dfb_registered_at = '2026-07-26'
    WHERE team_id = v_team_id AND member_id = (SELECT id FROM members WHERE passnummer = '0752-7665'); -- Yesiltas

    RAISE NOTICE 'E-Junioren roster updated: 2 removed, 11 dates updated';
END $$;
