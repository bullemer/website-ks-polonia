-- ============================================================
-- Migration 009: De-duplicate teams table
-- Merges duplicate teams (same mannschaftsname + division_id),
-- keeping the lowest ID and reassigning member_teams references.
-- Also adds a partial UNIQUE index to prevent future duplicates.
-- ============================================================

-- 1. Reassign member_teams from duplicate team IDs to the canonical (lowest) ID.
--    Uses ON CONFLICT to skip if the member is already assigned to the canonical team.
DO $$
DECLARE
    dup RECORD;
    canonical_id INT;
BEGIN
    -- Find groups of duplicate teams (same name + division, case-insensitive)
    FOR dup IN
        SELECT LOWER(mannschaftsname) as lname, division_id, MIN(id) as keep_id,
               ARRAY_AGG(id ORDER BY id) as all_ids
        FROM teams
        WHERE is_active = TRUE AND mannschaftsname IS NOT NULL
        GROUP BY LOWER(mannschaftsname), division_id
        HAVING COUNT(*) > 1
    LOOP
        canonical_id := dup.keep_id;
        RAISE NOTICE 'De-duplicating team "%" (division %): keeping id %, removing %',
            dup.lname, dup.division_id, canonical_id,
            array_to_string(ARRAY(SELECT unnest(dup.all_ids) EXCEPT SELECT canonical_id), ', ');

        -- Move member_teams assignments to canonical team (skip conflicts)
        UPDATE member_teams
        SET team_id = canonical_id
        WHERE team_id = ANY(dup.all_ids)
          AND team_id != canonical_id
          AND NOT EXISTS (
              SELECT 1 FROM member_teams mt2
              WHERE mt2.member_id = member_teams.member_id
                AND mt2.team_id = canonical_id
          );

        -- Delete orphaned member_teams that couldn't be moved (already exist on canonical)
        DELETE FROM member_teams
        WHERE team_id = ANY(dup.all_ids)
          AND team_id != canonical_id;

        -- Move treasury transactions
        UPDATE team_treasury_transactions
        SET team_id = canonical_id
        WHERE team_id = ANY(dup.all_ids)
          AND team_id != canonical_id;

        -- Move tasks
        UPDATE team_tasks
        SET team_id = canonical_id
        WHERE team_id = ANY(dup.all_ids)
          AND team_id != canonical_id;

        -- Soft-delete duplicate teams (keep data for audit trail)
        UPDATE teams
        SET is_active = FALSE,
            mannschaftsname = mannschaftsname || ' [DUPLICATE of #' || canonical_id || ']'
        WHERE id = ANY(dup.all_ids)
          AND id != canonical_id;
    END LOOP;
END $$;

-- 2. Add a partial unique index to prevent future duplicates
--    (only for active teams, case-insensitive)
CREATE UNIQUE INDEX IF NOT EXISTS idx_teams_unique_name_division
    ON teams (LOWER(mannschaftsname), division_id)
    WHERE is_active = TRUE;
