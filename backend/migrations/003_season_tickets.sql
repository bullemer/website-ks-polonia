-- ============================================================
-- KS Polonia – Season Ticket System
-- Database Migration v2.2
-- ============================================================

-- ════════════════════════════════════════
--  SEASON TICKET HOLDERS (Dauerkarten-Inhaber)
--  Separate from members — not necessarily club members
-- ════════════════════════════════════════
CREATE TABLE IF NOT EXISTS season_ticket_holders (
    id              SERIAL PRIMARY KEY,
    vorname         VARCHAR(100) NOT NULL,
    nachname        VARCHAR(100) NOT NULL,
    email           VARCHAR(255) NOT NULL UNIQUE,
    password_hash   VARCHAR(255),
    telefon         VARCHAR(50),
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sth_email ON season_ticket_holders(email);

-- ════════════════════════════════════════
--  SEASON TICKETS (Dauerkarten)
-- ════════════════════════════════════════
CREATE TABLE IF NOT EXISTS season_tickets (
    id              SERIAL PRIMARY KEY,
    holder_id       INT NOT NULL REFERENCES season_ticket_holders(id) ON DELETE CASCADE,
    season          VARCHAR(20) NOT NULL DEFAULT '2026/2027',
    ticket_code     VARCHAR(50) UNIQUE,       -- e.g. DK-2026-0001
    status          VARCHAR(20) DEFAULT 'pending',  -- pending, approved, rejected, revoked
    seat_info       VARCHAR(100),             -- optional seat/section
    price           NUMERIC(10,2),
    admin_notes     TEXT,
    reviewed_by     VARCHAR(200),
    approved_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(holder_id, season)
);

CREATE INDEX IF NOT EXISTS idx_st_holder ON season_tickets(holder_id);
CREATE INDEX IF NOT EXISTS idx_st_season ON season_tickets(season);
CREATE INDEX IF NOT EXISTS idx_st_status ON season_tickets(status);
CREATE INDEX IF NOT EXISTS idx_st_code ON season_tickets(ticket_code);

-- Sequence for ticket codes
CREATE SEQUENCE IF NOT EXISTS season_ticket_seq START WITH 1;

-- Auto-update trigger
DROP TRIGGER IF EXISTS trg_sth_updated_at ON season_ticket_holders;
CREATE TRIGGER trg_sth_updated_at
    BEFORE UPDATE ON season_ticket_holders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS trg_st_updated_at ON season_tickets;
CREATE TRIGGER trg_st_updated_at
    BEFORE UPDATE ON season_tickets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
