-- ============================================================
-- KS Polonia – Payment Tracking System
-- Database Migration v2.1
-- ============================================================

-- ════════════════════════════════════════
--  MEMBER PAYMENTS (Beitragszahlungen)
--  Manually entered by admins
-- ════════════════════════════════════════
CREATE TABLE IF NOT EXISTS member_payments (
    id              SERIAL PRIMARY KEY,
    member_id       INT NOT NULL REFERENCES members(id) ON DELETE CASCADE,
    amount          NUMERIC(10,2) NOT NULL,
    description     VARCHAR(255) NOT NULL DEFAULT 'Mitgliedsbeitrag',
    period          VARCHAR(50),          -- e.g. '2026-Q1', '2026-H1', '01/2026'
    payment_date    DATE NOT NULL DEFAULT CURRENT_DATE,
    payment_method  VARCHAR(50) DEFAULT 'Überweisung',  -- Überweisung, Bar, SEPA
    status          VARCHAR(20) DEFAULT 'received',     -- received, pending, refunded
    notes           TEXT,
    created_by      VARCHAR(200),         -- admin email who entered it
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_payments_member ON member_payments(member_id);
CREATE INDEX IF NOT EXISTS idx_payments_date ON member_payments(payment_date DESC);
CREATE INDEX IF NOT EXISTS idx_payments_period ON member_payments(period);

-- Auto-update trigger for updated_at
DROP TRIGGER IF EXISTS trg_payments_updated_at ON member_payments;
CREATE TRIGGER trg_payments_updated_at
    BEFORE UPDATE ON member_payments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
