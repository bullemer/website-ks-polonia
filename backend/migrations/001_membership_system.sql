-- ============================================================
-- KS Polonia – Membership Management System
-- Database Migration v2.0
-- Run against: kspolonia @ kwnz.your-database.de
-- ============================================================

-- ════════════════════════════════════════
--  1. DIVISIONS (Abteilungen)
-- ════════════════════════════════════════
CREATE TABLE IF NOT EXISTS divisions (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL UNIQUE,
    sport       VARCHAR(50)  NOT NULL,
    icon        VARCHAR(10)  DEFAULT '⚽',
    description TEXT,
    is_active   BOOLEAN      DEFAULT TRUE,
    sort_order  INT          DEFAULT 0,
    created_at  TIMESTAMPTZ  DEFAULT NOW()
);

-- Seed the four core divisions
INSERT INTO divisions (name, sport, icon, description, sort_order) VALUES
    ('Fußball',    'Fußball',    '⚽', 'Fußball-Abteilung – Herren, Jugend & Kinder', 1),
    ('Basketball', 'Basketball', '🏀', 'Basketball – Kinder U10 und Herren Ü35',       2),
    ('Badminton',  'Badminton',  '🏸', 'Badminton für Erwachsene',                     3),
    ('Volleyball', 'Volleyball', '🏐', 'Volleyball (in Gründung)',                     4)
ON CONFLICT (name) DO NOTHING;


-- ════════════════════════════════════════
--  2. TEAMS – Extend existing table
-- ════════════════════════════════════════
-- Add division_id FK and extra columns to the existing teams table.
-- Safe: uses ADD COLUMN IF NOT EXISTS (PG 9.6+).

DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'teams' AND column_name = 'division_id'
    ) THEN
        ALTER TABLE teams ADD COLUMN division_id INT REFERENCES divisions(id);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'teams' AND column_name = 'coach'
    ) THEN
        ALTER TABLE teams ADD COLUMN coach VARCHAR(200);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'teams' AND column_name = 'age_group'
    ) THEN
        ALTER TABLE teams ADD COLUMN age_group VARCHAR(50);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'teams' AND column_name = 'widget_id'
    ) THEN
        ALTER TABLE teams ADD COLUMN widget_id VARCHAR(100);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'teams' AND column_name = 'is_active'
    ) THEN
        ALTER TABLE teams ADD COLUMN is_active BOOLEAN DEFAULT TRUE;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'teams' AND column_name = 'sort_order'
    ) THEN
        ALTER TABLE teams ADD COLUMN sort_order INT DEFAULT 0;
    END IF;
END $$;

-- Backfill: assign existing teams to the Fußball division
UPDATE teams SET division_id = (SELECT id FROM divisions WHERE name = 'Fußball')
WHERE division_id IS NULL;


-- ════════════════════════════════════════
--  3. MEMBERS (Mitglieder)
-- ════════════════════════════════════════
CREATE TABLE IF NOT EXISTS members (
    id                      SERIAL PRIMARY KEY,
    mitgliedsnummer          VARCHAR(20) UNIQUE,
    vorname                  VARCHAR(100)  NOT NULL,
    nachname                 VARCHAR(100)  NOT NULL,
    email                    VARCHAR(255)  NOT NULL UNIQUE,
    password_hash            VARCHAR(255),
    telefon                  VARCHAR(50),
    strasse                  VARCHAR(255),
    plz                      VARCHAR(10),
    ort                      VARCHAR(100),
    land                     VARCHAR(100)  DEFAULT 'Deutschland',
    geburtsdatum             DATE,
    geschlecht               VARCHAR(20),
    eintrittsdatum           DATE,
    membership_level         VARCHAR(30)   DEFAULT 'regular',
    is_admin                 BOOLEAN       DEFAULT FALSE,
    is_active                BOOLEAN       DEFAULT TRUE,
    email_verified           BOOLEAN       DEFAULT FALSE,
    email_verify_token       VARCHAR(100),
    password_reset_token     VARCHAR(100),
    password_reset_expires   TIMESTAMPTZ,
    id_front_path            VARCHAR(500),
    id_back_path             VARCHAR(500),
    trainer_referenz         VARCHAR(200),
    bemerkungen              TEXT,
    created_at               TIMESTAMPTZ   DEFAULT NOW(),
    updated_at               TIMESTAMPTZ   DEFAULT NOW()
);

-- Index for fast email lookups (login)
CREATE INDEX IF NOT EXISTS idx_members_email ON members(email);
-- Index for membership number lookups
CREATE INDEX IF NOT EXISTS idx_members_mitgliedsnummer ON members(mitgliedsnummer);


-- ════════════════════════════════════════
--  4. MEMBER ↔ DIVISION (many-to-many)
-- ════════════════════════════════════════
CREATE TABLE IF NOT EXISTS member_divisions (
    id           SERIAL PRIMARY KEY,
    member_id    INT NOT NULL REFERENCES members(id) ON DELETE CASCADE,
    division_id  INT NOT NULL REFERENCES divisions(id) ON DELETE CASCADE,
    joined_at    DATE DEFAULT CURRENT_DATE,
    left_at      DATE,
    status       VARCHAR(20) DEFAULT 'active',  -- active, inactive, suspended
    UNIQUE(member_id, division_id)
);

CREATE INDEX IF NOT EXISTS idx_member_divisions_member ON member_divisions(member_id);
CREATE INDEX IF NOT EXISTS idx_member_divisions_division ON member_divisions(division_id);


-- ════════════════════════════════════════
--  5. MEMBER ↔ TEAM (many-to-many)
-- ════════════════════════════════════════
CREATE TABLE IF NOT EXISTS member_teams (
    id            SERIAL PRIMARY KEY,
    member_id     INT NOT NULL REFERENCES members(id) ON DELETE CASCADE,
    team_id       INT NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    position      VARCHAR(50),
    jersey_number INT,
    joined_at     DATE DEFAULT CURRENT_DATE,
    left_at       DATE,
    status        VARCHAR(20) DEFAULT 'active',  -- active, inactive, loaned
    UNIQUE(member_id, team_id)
);

CREATE INDEX IF NOT EXISTS idx_member_teams_member ON member_teams(member_id);
CREATE INDEX IF NOT EXISTS idx_member_teams_team ON member_teams(team_id);


-- ════════════════════════════════════════
--  6. BANK ACCOUNTS (SEPA / Bankverbindung)
-- ════════════════════════════════════════
CREATE TABLE IF NOT EXISTS member_bank_accounts (
    id                 SERIAL PRIMARY KEY,
    member_id          INT NOT NULL REFERENCES members(id) ON DELETE CASCADE,
    kontoinhaber       VARCHAR(200) NOT NULL,
    iban               VARCHAR(34)  NOT NULL,
    bic                VARCHAR(11),
    bank_name          VARCHAR(200),
    is_sepa_mandate    BOOLEAN      DEFAULT FALSE,
    sepa_mandate_date  DATE,
    sepa_mandate_ref   VARCHAR(50),
    is_active          BOOLEAN      DEFAULT TRUE,
    created_at         TIMESTAMPTZ  DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_bank_accounts_member ON member_bank_accounts(member_id);


-- ════════════════════════════════════════
--  7. MEMBERSHIP APPLICATIONS (Anträge)
-- ════════════════════════════════════════
CREATE TABLE IF NOT EXISTS membership_applications (
    id            SERIAL PRIMARY KEY,
    member_id     INT NOT NULL REFERENCES members(id) ON DELETE CASCADE,
    status        VARCHAR(20) DEFAULT 'pending',  -- pending, approved, rejected
    admin_notes   TEXT,
    reviewed_by   VARCHAR(200),
    submitted_at  TIMESTAMPTZ DEFAULT NOW(),
    reviewed_at   TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_applications_status ON membership_applications(status);
CREATE INDEX IF NOT EXISTS idx_applications_member ON membership_applications(member_id);


-- ════════════════════════════════════════
--  8. AUTO-UPDATE updated_at TRIGGER
-- ════════════════════════════════════════
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_members_updated_at ON members;
CREATE TRIGGER trg_members_updated_at
    BEFORE UPDATE ON members
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- ════════════════════════════════════════
--  9. MEMBER NUMBER SEQUENCE
-- ════════════════════════════════════════
-- Used to generate POL-2026-0001 style numbers.
CREATE SEQUENCE IF NOT EXISTS member_number_seq START WITH 1;


-- ════════════════════════════════════════
--  Done!
-- ════════════════════════════════════════
-- Verify with:  SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;
