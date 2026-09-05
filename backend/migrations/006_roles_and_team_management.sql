-- ============================================================
-- Migration 006: Three-Tier Role System & Team Management
-- Roles: superadmin, admin, member
-- Features: Mannschaftskasse (team treasury) & Team Tasks
-- ============================================================

-- 1. Add role column to members
DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'members' AND column_name = 'role'
    ) THEN
        ALTER TABLE members ADD COLUMN role VARCHAR(20) DEFAULT 'member';
    END IF;
END $$;

-- Update existing admins to superadmin
UPDATE members SET role = 'superadmin' WHERE is_admin = TRUE;
UPDATE members SET role = 'member' WHERE role IS NULL;

-- 2. Team Treasury / Mannschaftskasse
CREATE TABLE IF NOT EXISTS team_treasury_transactions (
    id SERIAL PRIMARY KEY,
    team_id INT NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    member_id INT REFERENCES members(id) ON DELETE SET NULL,
    type VARCHAR(20) NOT NULL, -- 'income', 'expense', 'fine'
    amount NUMERIC(10, 2) NOT NULL,
    description VARCHAR(255) NOT NULL,
    transaction_date DATE DEFAULT CURRENT_DATE,
    created_by INT REFERENCES members(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_team_treasury_team_id ON team_treasury_transactions(team_id);
CREATE INDEX IF NOT EXISTS idx_team_treasury_date ON team_treasury_transactions(transaction_date DESC);

-- 3. Team Tasks & Duties (Aufgaben, Dienste, Trikotwäsche, Fahrdienst etc.)
CREATE TABLE IF NOT EXISTS team_tasks (
    id SERIAL PRIMARY KEY,
    team_id INT NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    assigned_to INT REFERENCES members(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    due_date DATE,
    status VARCHAR(20) DEFAULT 'open', -- 'open', 'completed'
    completed_at TIMESTAMPTZ,
    created_by INT REFERENCES members(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_team_tasks_team_id ON team_tasks(team_id);
CREATE INDEX IF NOT EXISTS idx_team_tasks_assigned_to ON team_tasks(assigned_to);
