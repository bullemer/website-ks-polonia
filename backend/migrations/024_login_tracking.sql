-- Add login tracking columns to members
ALTER TABLE members ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMPTZ;
ALTER TABLE members ADD COLUMN IF NOT EXISTS login_count INTEGER DEFAULT 0;
