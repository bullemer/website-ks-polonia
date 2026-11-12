-- ============================================================
-- Migration 010: Player registration fields
-- Adds nationality, DFB pass number to members,
-- and Spielrecht / DFB registration dates to member_teams.
-- Also makes email nullable (minors / player-only members
-- won't have email addresses or login accounts).
-- ============================================================

-- 0. Make email nullable for player-only records (minors)
ALTER TABLE members ALTER COLUMN email DROP NOT NULL;
-- Replace the blanket UNIQUE with a partial one (only non-null emails must be unique)
ALTER TABLE members DROP CONSTRAINT IF EXISTS members_email_key;
CREATE UNIQUE INDEX IF NOT EXISTS idx_members_email_unique
    ON members (email) WHERE email IS NOT NULL;

-- 1. Add player identification fields to members
ALTER TABLE members ADD COLUMN IF NOT EXISTS nationality VARCHAR(5);
ALTER TABLE members ADD COLUMN IF NOT EXISTS passnummer  VARCHAR(20);

-- 1b. Claim token for self-registration (players/parents fill in email + phone)
ALTER TABLE members ADD COLUMN IF NOT EXISTS claim_token VARCHAR(100);

-- 2. Add DFB Spielrecht / registration tracking to member_teams
ALTER TABLE member_teams ADD COLUMN IF NOT EXISTS spielrecht_ab     DATE;
ALTER TABLE member_teams ADD COLUMN IF NOT EXISTS dfb_registered_at DATE;
ALTER TABLE member_teams ADD COLUMN IF NOT EXISTS passnummer_status VARCHAR(10);
  -- passnummer_status: e.g. 'P' (Pflichtspiel), 'F' (Freundschaftsspiel)

-- 3. Index for fast look-up by pass number
CREATE UNIQUE INDEX IF NOT EXISTS idx_members_passnummer
    ON members (passnummer)
    WHERE passnummer IS NOT NULL AND passnummer != '';
