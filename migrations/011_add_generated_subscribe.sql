-- Migration 011: Add generated_subscribe column
-- Created: 2025-10-30
-- Description: Add column for AI-generated subscribe text

-- Add generated_subscribe column
ALTER TABLE workflow_description_state ADD COLUMN IF NOT EXISTS generated_subscribe TEXT;

SELECT 'Migration 011 completed - generated_subscribe column added' AS status;

