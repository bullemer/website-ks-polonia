-- ============================================================
-- KS Polonia – Team role support
-- Migration v2.3
-- ============================================================

-- Add role column to member_teams (player, trainer, manager, co-trainer)
DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'member_teams' AND column_name = 'role'
    ) THEN
        ALTER TABLE member_teams ADD COLUMN role VARCHAR(30) DEFAULT 'player';
    END IF;
END $$;
