-- Migration 010: Cleanup legacy prompts
-- Created: 2025-10-30
-- Description: Remove unused individual prompts (about, what_to_expect, seo_tags)

-- We only need 2 prompts now:
-- 1. description_system (system) - Controls output format
-- 2. full_description (user) - Generates content

DELETE FROM ai_prompts WHERE name IN ('about', 'what_to_expect', 'seo_tags');

-- Verify we have the correct prompts
SELECT 
    name, 
    prompt_type, 
    description 
FROM ai_prompts 
ORDER BY prompt_type, name;

SELECT 'Migration 010 completed - Legacy prompts removed' AS status;

