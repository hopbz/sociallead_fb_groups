-- Migration: Sync lead_candidates table to match current model
-- Run this on existing databases that were created before the schema update

-- 1. Add missing columns (IF NOT EXISTS is safe to re-run)
ALTER TABLE lead_candidates
    ADD COLUMN IF NOT EXISTS group_name VARCHAR(255),
    ADD COLUMN IF NOT EXISTS group_url TEXT,
    ADD COLUMN IF NOT EXISTS post_url TEXT,
    ADD COLUMN IF NOT EXISTS author VARCHAR(255),
    ADD COLUMN IF NOT EXISTS content TEXT NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS need_stage VARCHAR(32),
    ADD COLUMN IF NOT EXISTS persona VARCHAR(255),
    ADD COLUMN IF NOT EXISTS pain_points TEXT,
    ADD COLUMN IF NOT EXISTS source VARCHAR(64) NOT NULL DEFAULT 'facebook_group';

-- 2. Migrate data from old columns to new ones if needed
UPDATE lead_candidates SET content = COALESCE(intent, '') WHERE content = '' AND intent IS NOT NULL;

-- 3. Fix status values (old schema used 'NEEDS_REVIEW', new schema uses 'new')
UPDATE lead_candidates SET status = 'new' WHERE status = 'NEEDS_REVIEW';
UPDATE lead_candidates SET status = 'reviewed' WHERE status = 'REVIEWED';
UPDATE lead_candidates SET status = 'contacted' WHERE status = 'CONTACTED';
UPDATE lead_candidates SET status = 'won' WHERE status = 'WON';
UPDATE lead_candidates SET status = 'lost' WHERE status = 'LOST';

-- 4. Set default score if score column exists but has wrong default
ALTER TABLE lead_candidates ALTER COLUMN score SET DEFAULT 1;

-- Done
SELECT 'Migration complete.' as result;
